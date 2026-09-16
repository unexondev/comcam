from enum import Enum

from .resolver import SensorResolver

from .impl import realsense # register realsense


class ApiNames(Enum):
    REALSENSE = "RealSense"


__all__ = [
    "SensorResolver",
    "ApiNames"
]