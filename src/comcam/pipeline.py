from dataclasses import dataclass
from collections import defaultdict

from comcam.stream import Stream, StreamProfile
from comcam.core.sensor import Sensor, SensorConfig, SensorState
from comcam.core.sensor.exceptions import *
from comcam.util.resolver import SPResolver
from comcam.util.resolver import PVID

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
                 options : PipelineOptions
                 ):
        
        self.opts = options
        self._prf_to_sensor : dict[StreamProfile, Sensor] = {}
        self.resolver = SPResolver()


    def _sensors(self):
        return list(dict.fromkeys(self._prf_to_sensor.values()))


    def add_config(self,
                  profiles : set[StreamProfile],
                  pvid_device : PVID | None = None
                  ) -> None:

        prf_to_ss = self._prf_to_sensor

        prf_to_ss_new : dict[StreamProfile, Sensor] = {}

        for profile in profiles:

            if profile in prf_to_ss:
                # remove configuration if exists
                self.remove_config(profile)

            sensor = self.resolver.resolve(
                stream_profile=profile,
                pvid=pvid_device
                )

            if sensor is None:
                raise RuntimeError(
                    "Could not resolve a sensor for stream profile:\n\t%r\nand PVID:\n\t%r." % (profile, pvid_device)
                    )

            prf_to_ss_new[profile] = sensor # do the mapping

        sensor_profiles : defaultdict[Sensor, set[StreamProfile]] = defaultdict(set)
        for profile, sensor in prf_to_ss_new.items():

            sensor_profiles[sensor].add(profile)

        for sensor, _profiles in sensor_profiles.items():

            sensor.configure(SensorConfig(
                stream=Stream(),
                stream_profiles=frozenset(_profiles)
            ))

        prf_to_ss.update(prf_to_ss_new) # update the mapping


    def remove_config(self, profile : StreamProfile) -> None:
        sensor = self._prf_to_sensor.pop(profile)


    def start(self, stream_profile : StreamProfile | None = None) -> None:

        if not self._prf_to_sensor:
            raise RuntimeError(
                "Sensor not found, please configure pipeline before starting it."
                )

        # get sensors only 'once' if stream profile is not given
        sensors = self._sensors() if stream_profile is None else [
                self._prf_to_sensor[stream_profile]
            ]

        for sensor in sensors:

            if sensor.state != SensorState.CLOSED:
                raise RuntimeError("Sensor has been already opened or streaming.")

            # open the sensor
            sensor.open()

            # start the sensor
            sensor.start()


    def stop(self, stream_profile : StreamProfile | None = None) -> None:

        # get sensors only 'once' if stream profile is not given
        sensors = self._sensors() if stream_profile is None else [
                self._prf_to_sensor[stream_profile]
            ]

        for sensor in sensors:

            if sensor.state != SensorState.STREAMING:
                raise RuntimeError("Sensor has not been streaming.")

            # open the sensor
            sensor.open()

            # start the sensor
            sensor.start()
        

    def alive(self, stream_profile : StreamProfile | None = None):

        # get sensors only 'once' if stream profile is not given
        sensors = self._sensors() if stream_profile is None else [
                self._prf_to_sensor[stream_profile]
            ]

        return bool(sensors) and all(
            sensor.state == SensorState.STREAMING for sensor in sensors
            )


    def sensor(self, stream_profile : StreamProfile | None = None) -> Sensor:
        return self._prf_to_sensor[stream_profile]


    def stream(self, stream_profile : StreamProfile) -> Stream:
        return self._prf_to_sensor[stream_profile].config.stream