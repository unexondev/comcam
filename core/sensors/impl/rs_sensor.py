from ..sensor import Sensor
from ...stream_profile import StreamProfile

from pyrealsense2 import sensor as rs2_sensor, stream_profile


class RSSensor(Sensor):

    def __init__(self,
                 sensor : rs2_sensor,
                 ):

        # initialize Sensor base class
        super().__init__()

        # store the pyrealsense2 sensor object
        self._sensor = sensor


    def resolve_rs_stream_profiles(self) -> set[StreamProfile]:

        rs_profiles : set[StreamProfile] = set()

        for prf_supported in self._sensor.profiles:
            for prf_requested in self.profiles:

                if prf_requested == prf_supported:
                    rs_profiles.add(prf_supported)

        return rs_profiles


    def open(self):
        # check if profiles are given
        if not self.profiles:
            raise RuntimeError(
                "Realsense2's sensor API requires profiles"
                " to be given before opening the sensor."
                )
        rs_profiles = self.resolve_rs_stream_profiles()
        

    def start(self):
        """
        Start the sensor (start streaming) physically.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop the sensor (end streaming) physically.
        """
        raise NotImplementedError()

    def is_opened(self):
        """
        Check if sensor is physically in `Opened` state.
        """
        raise NotImplementedError()

    def is_closed(self):
        """
        Check if sensor is physically in `Closed` state.
        """
        return not self.is_opened()
