from typing import Callable
from collections.abc import Iterator

from comcam.stream.profile import StreamProfile
from comcam.core.sensor import Sensor


class SensorResolverInterface:

    @classmethod
    def resolve(cls, stream_profile : StreamProfile) -> Iterator[Sensor]:
        raise NotImplementedError()


    @classmethod
    def resolve_all(cls) -> Iterator[Sensor]:
        raise NotImplementedError()


class SensorResolver:
    """
    Utilization class that resolves stream profiles to sensors.

    Guarantees that 'Sensor' instance will be
    created once for each sensor by _caching_ them. 
    """

    api_resolvers : dict[str, type[SensorResolverInterface]] = {}

    _sensor_cache : dict[Sensor, Sensor] = {}


    @classmethod
    def register(cls,
                 name : str,
                 resolver : type[SensorResolverInterface]
                 ) -> None:
        cls.api_resolvers[name] = resolver


    @classmethod
    def resolve(cls,
                stream_profile : StreamProfile,
                api_name : str | None = None
                ) -> Iterator[Sensor]:
        """
        Resolves all the sensors that are capable of stream in given stream profile.

        Args:
            stream_profile: A `StreamProfile` instance to check that is streamable while discovering sensors.
            api_name (optional): Name of API to resolve from. If None, all of the APIs are included.
            
        Returns:
            An iterator of 'Sensor' objects.
        """

        for _api_name, ResolverImpl in cls.api_resolvers.items():

            if api_name is not None and api_name != _api_name:
                continue

            for sensor in ResolverImpl.resolve(stream_profile):

                cached = cls._sensor_cache.get(sensor)

                if cached is None:
                    cls._sensor_cache[sensor] = sensor # save it to cache
                    cached = sensor

                yield cached # return it


    @classmethod
    def resolve_all(cls, api_name : str | None = None):
        """
        Resolves all the sensors.

        Args:
            api_name (optional): Name of API to resolve from. If None, all of the APIs are included.
        
        Returns:
            An iterator of 'Sensor' objects.
        """

        for _api_name, ResolverImpl in cls.api_resolvers.items():

            if api_name is not None and api_name != _api_name:
                continue

            for sensor in ResolverImpl.resolve_all():

                cached = cls._sensor_cache.get(sensor)

                if cached is None:
                    cls._sensor_cache[sensor] = sensor # save it to cache
                    cached = sensor

                yield cached # return it