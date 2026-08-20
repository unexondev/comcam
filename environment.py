from pyrealsense2 import context, option, syncer
from pyrealsense2 import stream_profile as rs_stream_profile
from pyrealsense2 import video_stream_profile as rs_video_stream_profile

from .core.sensor import Sensor
from .core.mixins.optimization import OptimizationMixin
from .stream.profile import StreamProfile

from dataclasses import dataclass
from enum import Enum

from threading import Lock # for thread-safe

import logging

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentOptions:

    optimized_startup : bool
    """
    If this option set to `True`, stereo module (depth sensors) is going to be heaten
    before running workers and so on.
    """

    asic_temp_range_stereo : tuple[float, float]
    """
    Optimal ASIC temperature range for depth sensors to establish accuracy and safety.
    On initialization step, depth sensors are going to be heaten before running workers
    until the given 'minimum' optimal temperature value is reached. On the other hand, if the
    temperature exceeds the given 'maximum' optimal temperature value, the pipeline will be suspended.
    """

    projector_temp_range_stereo : tuple[float, float]
    """
    Optimal project temperature range for depth sensors to establish accuracy and safety.
    On initialization step, depth sensors are going to be heaten before running workers
    until the given 'minimum' optimal temperature value is reached. On the other hand, if the
    temperature exceeds the given 'maximum' optimal temperature value, the pipeline will be suspended.
    """


class SensorState(Enum):
    CLOSED = 0,
    OPTIMIZING = 1,
    OPENED = 2,
    STARTED = 3,
    ERRORED = 4


class Environment(OptimizationMixin):
    """
    Manage all the devices required to receive data for given video stream profiles
    """

    @dataclass
    class SensorContext:
        sensor : Sensor
        profile : rs_stream_profile
        def __hash__(self):
            return hash((
                self.sensor, self.profile
            ))

    def __init__(self,
                 profile_to_sensor_ctx : dict[StreamProfile, SensorContext],
                 options : EnvironmentOptions
                 ):
        self._prf_to_sensor_ctx = profile_to_sensor_ctx # profile to sensor map
        self._sensor_states = {
            ctx_sensor.sensor: SensorState.CLOSED
                for ctx_sensor in profile_to_sensor_ctx.values()
            } # sensor to its state map
        self.opts = options
        self._lock = Lock() # for thread-safe read/writes to sensor states etc.

    @classmethod
    def create(cls, context : context, stream_profiles : set[StreamProfile], options : EnvironmentOptions):
        prf_to_sensor_ctx = {}

        # map profiles with sensors
        # FIXME
        sensors = context.query_all_sensors()
        prfs_not_found = stream_profiles.copy()
        for sensor in sensors:

            rs_prfs_stream = sensor.get_stream_profiles()
            for rs_prf_stream in rs_prfs_stream:

                if not prfs_not_found: break

                for prf_stream in prfs_not_found:

                    if not rs_prf_stream.is_video_stream_profile():
                        continue

                    rs_prf_stream : rs_video_stream_profile \
                        = rs_prf_stream.as_video_stream_profile()

                    if prf_stream.matches(rs_prf_stream):

                        prf_to_sensor_ctx[prf_stream] = cls.SensorContext(sensor, rs_prf_stream)

                        prfs_not_found.remove(prf_stream)

                        break

            else:
                continue

            break

        else:
            raise RuntimeError("Some of the stream profiles are not supported")

        return cls(
            profile_to_sensor_ctx=prf_to_sensor_ctx,
            options=options
            )


    def _get_rs_stream_profile(self, stream_profile : StreamProfile):
        return self._prf_to_sensor_ctx[stream_profile].profile


    def _get_sensor_state(self, sensor : rs_sensor):
        with self._lock:
            return self._sensor_states[sensor]


    def _set_sensor_state(self, sensor : rs_sensor, state : SensorState):
        with self._lock:
            self._sensor_states[sensor] = state


    """
    Helper functions while interacting with sensors
    """

    def get_sensor(self, stream_profile : StreamProfile):
        return self._prf_to_sensor_ctx[stream_profile].sensor


    def stream_profiles(self):
        for prf in self._prf_to_sensor_ctx.keys():
            prf : StreamProfile
            yield prf


    def sensors(self):
        for ctx_sensor in set(self._prf_to_sensor_ctx.values()):
            yield ctx_sensor.sensor


    def is_streaming(self, stream_profile : StreamProfile):
        sensor = self.get_sensor(stream_profile)
        return self._get_sensor_state(sensor) == SensorState.STARTED


    def check_health(self):

        for sensor in self.sensors():

            if self._get_sensor_state(sensor) != SensorState.STARTED:
                continue # sensor must be streaming to check its health

            if sensor.is_depth_sensor():
                """
                - Asic temperature
                - Projector temperature
                """
                opts_sensor = sensor.get_supported_options()
                if option.asic_temperature in opts_sensor:
                    asic_temp = sensor.get_option(option.asic_temperature)
                    asic_temp_max = self.opts.asic_temp_range_stereo[1]

                    if asic_temp > asic_temp_max:
                        return False

                if option.projector_temperature in opts_sensor:
                    projector_temp = sensor.get_option(option.projector_temperature)
                    projector_temp_max = self.opts.projector_temp_range_stereo[1]

                    if projector_temp > projector_temp_max:
                        return False

        # TODO add health checks for other type of sensors?

        return True
    

    def start_stream(self, stream_profile : StreamProfile, syncer : syncer = None):
        """
        Begins streaming by starting the sensor.

        Args:
            stream_profile: A StreamProfile instance indicates which stream to be started.
        """
        sensor = self.get_sensor(stream_profile)
        rs_prf_stream = self._get_rs_stream_profile(stream_profile)

        logger.debug("Attempting to start sensor %X "
                     "with syncer %s..." %
                     (id(sensor), "%X" % id(syncer) if syncer is not None else "`None`"))

        if self.opts.optimized_startup:
            self._set_sensor_state(
                sensor, SensorState.OPTIMIZING
                ) # set sensor state being optimized
            try:
                self.apply_optimizations(sensor) # apply optimizations to the sensor
                self._set_sensor_state(
                    sensor, SensorState.CLOSED
                    )
            except RuntimeError:
                self._set_sensor_state(
                    sensor, SensorState.ERRORED
                    )

        if self._is_sensor_opened_internal(sensor):
            if rs_prf_stream not in sensor.get_active_streams():
                # sensor is already opened with another stream profile
                logger.error("Sensor %X has already been opened "
                             "with different stream profile." % id(sensor))
                self._set_sensor_state(sensor, SensorState.ERRORED)
                raise
            pass # sensor is opened with given stream profile, go to starting process

        else: # sensor is not opened
            # try to open with given profile
            try:
                sensor.open(rs_prf_stream)
                self._set_sensor_state(sensor, SensorState.OPENED)
            except RuntimeError:
                # couldn't open
                logger.error("Couldn't open sensor %X. (internal error)" % id(sensor))
                self._set_sensor_state(sensor, SensorState.ERRORED)
                raise

        # starting process

        # check if already stopped
        if self._get_sensor_state(sensor) != SensorState.STARTED:
            # try to start
            try:
                sensor.start(syncer)
                self._set_sensor_state(sensor, SensorState.STARTED)
            except RuntimeError:
                # couldn't start
                logger.error("Couldn't start sensor %X. (internal error)" % id(sensor))
                self._set_sensor_state(sensor, SensorState.ERRORED)
                raise

        # started successfully
        logger.info("Sensor %X has been started successfully." % id(sensor))
    
        
    def stop_stream(self, stream_profile : StreamProfile):
        """
        Ends the stream by stopping the sensor.

        Args:
            stream_profile: A `StreamProfile` instance indicating which sensor to be stopped.
        """
        sensor = self.get_sensor(stream_profile)

        logger.debug("Attempting to stop sensor %X..." % id(sensor))

        if self._get_sensor_state(sensor) != SensorState.STARTED:
            return # nothing to do if not started

        try: 
            sensor.stop()
            self._set_sensor_state(sensor, SensorState.OPENED)
        except RuntimeError:
            # couldn't stop
            logger.error("Couldn't stop sensor %X. (internal error)" % id(sensor))
            self._set_sensor_state(sensor, SensorState.ERRORED)
            raise

        # stopped successfully
        logger.info("Sensor %X has been stopped successfully." % id(sensor))


    def start_all(self, syncer : syncer = None):
        """
        Starts all the streams by starting related sensors.

        Args:
            syncer: A `pyrealsense2.syncer` instance to synchronize frames.
        """
        for prf in self.stream_profiles():

            try:
                self.start_stream(prf, syncer)

            except RuntimeError:

                self.stop_all() # stop all if some of them couldn't be started

                raise


    def stop_all(self):
        """
        Ends all the streams by stopping related sensors.
        """
        for prf in self.stream_profiles():

            self.stop_stream(prf) 