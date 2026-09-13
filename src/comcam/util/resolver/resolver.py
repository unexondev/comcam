from typing import Callable
from collections.abc import Iterator

from comcam.stream.profile import StreamProfile
from comcam.core.sensor import Sensor


class SensorResolver:
    """
    Utilization class that resolves stream profiles to sensors.

    Guarantees that 'Sensor' instance will be
    created once for each sensor by _caching_ them. 
    """
    TyResolver = Callable[[ StreamProfile ], Iterator[ Sensor ]]

    api_resolvers : dict[str, TyResolver] = {}

    _sensor_cache : dict[Sensor, Sensor] = {}


    @classmethod
    def register(cls,
                 name : str,
                 resolver : TyResolver
                 ) -> None:
        cls.api_resolvers[name] = resolver


    @classmethod
    def resolve(cls,
                stream_profile : StreamProfile,
                api_name : str | None = None
                ) -> Iterator[Sensor]:
        """
        Resolves all the sensors that are capable of stream in 'all' of the given stream profiles.

        Args:
            stream_profiles: A set of `StreamProfile` objects to check that are streamable while discovering sensors.
        
        Returns:
            An iterator of 'Sensor' objects.
        """

        for _api_name, resolver in cls.api_resolvers.items():

            if api_name is not None and api_name != _api_name:
                continue

            for sensor in resolver(stream_profile):

                cached = cls._sensor_cache.get(sensor)

                if cached is None:
                    cls._sensor_cache[sensor] = sensor # save it to cache
                    cached = sensor

                yield cached # return it