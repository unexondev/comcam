from eyebin.stream.profile import StreamProfile
from eyebin.core.sensor import Sensor, SensorOptions


class SensorResolver:
    """
    Abstraction class for dependency resolution
    from stream profiles to all types of sensors.
    """

    def __init__(self, sensor_options : SensorOptions):
        self.opts_sensor = sensor_options

    def resolve(self, stream_profile : StreamProfile) -> Sensor | None:
        """
        Resolve the sensor that is dependent on for given stream profiles.

        Args:
            stream_profile: A StreamProfile object to check that is streamable while discovering sensors. 
        
        Returns:
            The first occurence of `Sensor` object
            if there is any sensor that is able to stream in given stream profile,
            `None` otherwise.
        """
        raise NotImplementedError()