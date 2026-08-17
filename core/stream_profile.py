from dataclasses import dataclass
from pyrealsense2 import stream as StreamType
from pyrealsense2 import format as StreamFormat
from pyrealsense2 import video_stream_profile


@dataclass
class StreamProfile:
    stream_type : StreamType
    format : StreamFormat


@dataclass
class VideoStreamProfile(StreamProfile):

    width : int
    height : int
    fps : int

    def __eq__(self, cmp):

        if isinstance(cmp, VideoStreamProfile):
            return self.stream_type == cmp.stream_type and \
                self.format == cmp.format and \
                self.width == cmp.width and \
                self.height == cmp.height and \
                self.fps == cmp.fps
            
        elif isinstance(cmp, video_stream_profile):
            return self.stream_type == cmp.stream_type() and \
                self.format == cmp.format() and \
                self.width == cmp.width() and \
                self.height == cmp.height() and \
                self.fps == cmp.fps()
        
        return NotImplemented

    def __hash__(self):
        return hash((
            self.width, self.height, self.fps,
            self.stream_type, self.format
            ))