from dataclasses import dataclass

from comcam.core.sensor.sensor import *
from comcam.core.sensor.exceptions import *

# Realsense implementations
from comcam.util.formatter.impl.realsense import RSFormatter
from comcam.stream.profile.lifter.impl.realsense import RSProfileLifter

# Realsense API
from pyrealsense2 import sensor as rs2_sensor
from pyrealsense2 import frame as rs2_frame
from pyrealsense2 import option as rs2_option
from pyrealsense2 import camera_info as rs2_camera_info
from pyrealsense2 import stream_profile as rs2_stream_profile

# util packages
import numpy


@dataclass
class RSSensorOptions(SensorOptions):
    # define thresholds
    max_asic_temperature : float = 40.0
    """
    Maximum ASIC temperature value allowed for depth sensors.
    If this value is exceeded, related sensor will be suspended.
    """
    max_projector_temperature : float = 40.0
    """
    Maximum projector temperature value allowed for depth sensors.
    If this value is exceeded, related sensor will be suspended.
    """


class RSSensor(Sensor):

    def __init__(self,
                 sensor : rs2_sensor,
                 device_desc : DeviceDesc,
                 options : RSSensorOptions,
                 config : SensorConfig | None = None
                 ):

        # initialize Sensor base class
        super().__init__(
            device_desc=device_desc,
            options=options,
            config=config
        )

        # store the pyrealsense2 sensor instance
        self._sensor = sensor

        # create profile map
        self._profile_map : dict[rs2_stream_profile, StreamProfile] = {}


    def __hash__(self):

        return hash((
            self.device,
            self._sensor.get_info(rs2_camera_info.name) # name of sensor, not device
        ))


    def __eq__(self, other):

        if not isinstance(other, RSSensor):
            return NotImplemented

        return (self.device == other.device and
                (self._sensor.get_info(rs2_camera_info.name) 
                 == other._sensor.get_info(rs2_camera_info.name))) 


    def open(self):

        with self._lock:

            # check if sensor is configured
            self._sanity_check_open()

            # check if already open
            if self._state != SensorState.CLOSED:
                raise RuntimeError(
                    "Sensor must be closed before opening."
                    )

            # prepare to open
            self._prepare_open()

            # get realsense stream profiles
            profiles_rs = list(self._profile_map.keys())
            if not profiles_rs:
                # fake (empty) stream can occur,
                # we don't want that
                raise RuntimeError(
                    "No stream profiles are passed, please configure sensor properly."
                    )

            # open the sensor
            try:
                self._sensor.open(profiles=profiles_rs)
                super().open()

            except RuntimeError as err:
                self._fail()
                raise SensorOpenError(
                    "Failed to open RealSense sensor."
                    ) from err 


    def close(self):

        with self._lock:

            if self._state != SensorState.OPENED:
                raise RuntimeError(
                    "Sensor must be opened before closing."
                    )

            # close the sensor directly
            try:
                self._sensor.close()
                super().close()

            except RuntimeError as err:
                self._fail()
                raise SensorCloseError(
                    "Failed to close RealSense sensor."
                    ) from err


    def start(self):

        with self._lock:

            if self._state != SensorState.OPENED:
                raise RuntimeError(
                    "Sensor must be opened before starting."
                    )

            # try to start the sensor
            try:
                # start sensor with our producer callback
                self._sensor.start(
                    callback=self._produce_stream_data
                )

                super().start()

            except RuntimeError as err:
                self._fail()
                raise SensorStartError(
                    "Failed to start RealSense sensor."
                    ) from err 


    def stop(self):

        with self._lock:

            if self._state != SensorState.CLOSED:
                raise RuntimeError(
                    "Sensor must be started before stopping."
                    )

            # stop the sensor directly
            try:
                self._sensor.stop()
                super().stop()

            except RuntimeError as err:
                self._fail()
                raise SensorStopError(
                    "Failed to stop RealSense sensor."
                    ) from err


    def is_healthy(self):

        ss = self._sensor
        opts = self.opts

        with self._lock:

            if self._state != SensorState.STREAMING:
                # for Realsense API, sensor must be
                # streaming to check its health, if not;
                # just return `True`.`
                return True

            # TODO: do we need another abstraction here?
            # suggestion: RSDepthSensor maybe?
            if ss.is_depth_sensor():
                """
                - Asic temperature
                - Projector temperature
                """
                opts_sensor = ss.get_supported_options()
                if rs2_option.asic_temperature in opts_sensor:

                    asic_temp = ss.get_option(rs2_option.asic_temperature)

                    if asic_temp > opts.max_asic_temperature:
                        return False

                if rs2_option.projector_temperature in opts_sensor:

                    projector_temp = ss.get_option(rs2_option.projector_temperature)

                    if projector_temp > opts.max_projector_temperature:
                        return False

            return True


    def _prepare_open(self):

        for profile_requested in self._conf.profiles_iter():

            for rs_profile_supported in self._sensor.profiles:

                if self.rs_profile_matches(rs_profile_supported, profile_requested):

                    self._profile_map[rs_profile_supported] = profile_requested

                    break # requested profile is mapped go next

            else:
                raise SPNotSupportedError(
                    "Stream profile %r not supported by sensor." % profile_requested
                    )


    def _produce_stream_data(self, frame : rs2_frame):

        with self._lock:

            prf_stream = self._profile_map[frame.profile]
            stream = self._conf.get_stream(prf_stream)

            data = frame.get_data() # get data

            stream.put(
                RSFormatter.convert_to(
                    numpy.asanyarray(data), # convert to numpy array first
                    frame.profile.format(),
                    self._profile_map[frame.profile].format
                    )
                ) # put data to stream


    @staticmethod
    def rs_profile_matches(rs_stream_profile : rs2_stream_profile,
                           stream_profile : StreamProfile
                           ) -> bool:
        
        fmt_rs = rs_stream_profile.format()

        sp_lifted = None
        try:
            sp_lifted = RSProfileLifter.lift(rs_stream_profile)
        except NotImplementedError:
            return False

        # RS profile matches with stream profile if:
        # - both have same frame rate &
        # - both represents same frame &
        # - RS profile's format is convertable to requested profile's
        return (
            sp_lifted.fps == rs_stream_profile.fps() and
            sp_lifted.get_frame() == stream_profile.get_frame() and
            RSFormatter.convertible_to(fmt_rs, stream_profile.format)
            )