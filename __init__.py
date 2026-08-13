# Realsense API
import pyrealsense2 as rs

# User APIs
from .pipeline import Pipeline
from .environment import Environment, EnvironmentOptions
from .stream import Stream, StreamOptions
from .core.stream_profile import *


def create_context() -> rs.context:
    return rs.context()