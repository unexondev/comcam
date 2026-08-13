from dataclasses import dataclass
from pyrealsense2 import stream as StreamType
from pyrealsense2 import format as StreamFormat


@dataclass
class StreamProfile:
    stream_type : StreamType
    format : StreamFormat


@dataclass
class VideoStreamProfile(StreamProfile):
    width : int
    height : int
    fps : int
    def __hash__(self):
        return hash((
            self.width, self.height, self.fps,
            self.stream_type, self.format
            ))