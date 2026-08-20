# Realsense API
import pyrealsense2 as rs

# User APIs
from .pipeline import Pipeline
from .environment import Environment, EnvironmentOptions
from .stream.stream import Stream, StreamOptions
from .stream.profile import *


def create_context() -> rs.context:
    return rs.context()