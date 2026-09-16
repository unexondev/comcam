from typing import Iterable, Callable, Any
from collections import defaultdict

from comcam.stream.profile import StreamFormat

from numpy.typing import NDArray


class Formatter:

    converters : defaultdict[
        Any, # source format
        dict[StreamFormat, Callable[[NDArray], NDArray]] # converter
        ]
    """
    A mapping from source types to converter mappings.
    """

    @classmethod
    def get_converters(
        cls,
        source_format : Any
        ) -> Iterable[
            tuple[StreamFormat, Callable[[NDArray], NDArray]]
        ]:

        converters = cls.converters.get(source_format)

        if converters is None:
            raise RuntimeError(
                "No conversion exist from %r to any format." % source_format
                )
        
        return converters.items()
    

    @classmethod
    def convertible_to(cls,
                    source_format : Any,
                    destination_format : StreamFormat
                    ):

        converters = cls.converters.get(source_format)
        return converters is not None and destination_format in converters


    @classmethod
    def convertible(cls, source_format : Any):
        converters = cls.converters.get(source_format)
        return bool(converters)


    @classmethod
    def add_converter(cls,
                      source_format : Any,
                      destination_type : StreamFormat,
                      converter : Callable[[Any], NDArray]
                      ):
        
        cls.converters[source_format][destination_type] = converter


    @classmethod
    def convert_to(cls,
                source_data : NDArray,
                source_format : Any,
                destination_format : StreamFormat
                ) -> NDArray:
        converter = cls.converters.get(source_format, {}).get(destination_format)
        if converter is None:
            raise RuntimeError("Unsupported conversion: %r -> %r"
                               % (source_format, destination_format))

        return converter(source_data)


    @staticmethod
    def _convert_alias(source_data : NDArray):
        return source_data