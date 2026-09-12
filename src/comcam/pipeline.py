from dataclasses import dataclass

from comcam.stream import Stream, StreamProfile
from comcam.core.sensor import Sensor, SensorConfig, SensorState
from comcam.core.sensor.exceptions import *
from comcam.util.resolver import SensorResolver

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler()]
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineOptions:
    pass

        
class Pipeline:
    """
    The main pipeline that organizes tasks.
    """

    def __init__(self,
                 options : PipelineOptions,
                 resolver : SensorResolver = None
                 ):
        
        self.opts = options
        self._prf_to_sensor : dict[StreamProfile, Sensor] = {}
        self.resolver = SensorResolver() if resolver is None else resolver


    def sensors(self):

        return list(dict.fromkeys(self._prf_to_sensor.values()))


    def get_sensor(self, stream_profile : StreamProfile):

        return self._prf_to_sensor[stream_profile]


    def create_stream(self, 
                      stream_profile : StreamProfile,
                      sensor : Sensor | None = None
                      ) -> Stream:

        prf_to_ss = self._prf_to_sensor

        if stream_profile in prf_to_ss:
            # remove configuration if exists
            self.remove_stream(stream_profile)

        # resolve sensor if not given
        sensor = next(
            self.resolver.resolve(stream_profile), None
            ) if sensor is None else sensor
        
        if sensor is None:
            raise RuntimeError(
                "Could not resolve a sensor for stream profile: %r" % stream_profile
                )

        # create stream
        stream = Stream()

        # tell sensor to use that
        sensor.config.use(stream_profile, stream)

        # map it to the profile
        prf_to_ss[stream_profile] = sensor

        return stream


    def remove_stream(self, stream_profile : StreamProfile) -> None:

        sensor = self._prf_to_sensor.pop(stream_profile, None)

        if sensor is None:
            raise RuntimeError(
                "Stream profile %r doesn't exist "
                "in current stream profiles." % stream_profile)

        if sensor.state != SensorState.CLOSED:
            raise RuntimeError(
                "Sensor must be closed to mutate its config."
                )

        sensor.config.remove(stream_profile)

    def start(self, sensor : Sensor | None = None) -> None:

        if not self._prf_to_sensor:
            raise RuntimeError(
                "Sensor not found, please configure pipeline before starting it."
                )

        # get sensors only 'once' if stream profile is not given
        sensors = self.sensors() if sensor is None else [ sensor ]

        for _sensor in sensors:

            if _sensor.state != SensorState.CLOSED:
                raise RuntimeError("Sensor has been already opened or streaming.")

            # open the sensor
            _sensor.open()

            # start the sensor
            _sensor.start()


    def stop(self, sensor : Sensor | None = None) -> None:

        # get sensors only 'once' if stream profile is not given
        sensors = self.sensors() if sensor is None else [ sensor ]

        for _sensor in sensors:

            if _sensor.state != SensorState.STREAMING:
                raise RuntimeError("Sensor has not been streaming.")

            # stop the sensor
            _sensor.stop()

            # close the sensor
            _sensor.close()


    def alive(self, sensor : Sensor | None = None):

        # get sensors only 'once' if stream profile is not given
        sensors = self.sensors() if sensor is None else [ sensor ]

        return bool(sensors) and all(
            _sensor.state == SensorState.STREAMING for _sensor in sensors
            )


    def sensor(self, stream_profile : StreamProfile | None = None) -> Sensor:
        return self._prf_to_sensor[stream_profile]


    def stream(self, stream_profile : StreamProfile) -> Stream:
        sensor = self._prf_to_sensor[stream_profile]
        return sensor.config.get_stream(stream_profile)