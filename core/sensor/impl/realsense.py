from typing import Callable
from dataclasses import dataclass

from eyebin.core.sensor import Sensor, SensorOptions
from eyebin.core.sensor.sensor import SensorState
from eyebin.core.sensor.exceptions import *
from eyebin.stream import StreamProfile

# Realsense API
from pyrealsense2 import sensor as rs2_sensor
from pyrealsense2 import syncer as rs2_syncer
from pyrealsense2 import frame as rs2_frame
from pyrealsense2 import option as rs2_option

# util packages
import numpy


@dataclass
class RSSensorOptions(SensorOptions):
    # define thresholds
    max_asic_temperature : float
    """
    Maximum ASIC temperature value allowed for depth sensors.
    If this value is exceeded, related sensor will be suspended.
    """
    max_projector_temperature : float
    """
    Maximum projector temperature value allowed for depth sensors.
    If this value is exceeded, related sensor will be suspended.
    """


class RSSensor(Sensor):

    def __init__(self,
                 sensor : rs2_sensor,
                 options : RSSensorOptions
                 ):

        # initialize Sensor base class
        super().__init__(
            options=options
            )

        # store the pyrealsense2 sensor instance
        self._sensor = sensor


    def _resolve_rs_stream_profiles(self) -> set[StreamProfile]:

        rs_profiles : set[StreamProfile] = set()

        for prf_supported in self._sensor.profiles:
            for prf_requested in self._profiles:

                if prf_requested.matches(prf_supported):
                    rs_profiles.add(prf_supported)

        return rs_profiles


    def open(self):
        # check if profiles are given
        if not self.profiles:
            raise RuntimeError(
                "Realsense2's sensor API requires profiles"
                " to be given before opening the sensor."
                )

        # retrieve pyrealsense2 stream profiles
        rs_profiles = self._resolve_rs_stream_profiles()

        # open the sensor
        try:
            self._sensor.open(profiles=rs_profiles)
            super().open()

        except RuntimeError as err:
            self._fail()
            raise SensorOpenError(
                "Failed to open RealSense sensor."
                ) from err 


    def close(self):
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
        # start the sensor directly
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
        # stop the sensor directly
        try:
            self._sensor.stop()
            super().stop()

        except RuntimeError as err:
            self._fail()
            raise SensorStopError(
                "Failed to stop RealSense sensor."
                ) from err


    def is_opened(self):
        try:
            return len(self._sensor.get_active_streams()) > 0

        except RuntimeError as err:
            self._fail()
            raise SensorInfoError(
                "Failed to gather information from sensor."
            ) from err


    def is_healthy(self):

        ss = self._sensor
        opts = self.opts

        with self._lock:

            if self.state != SensorState.STREAMING:
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


    def _produce_stream_data(self, frame : rs2_frame):
        stream = self._stream
        if stream is None:
            return # no outgoing stream

        data = frame.get_data()

        stream.put(data) # put data to stream