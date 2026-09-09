from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StreamFormat(Enum):
    """
    Common stream formats
    """
    GRAY8 = "gray8"
    GRAY16 = "gray16"
    RGB8 = "rgb8"
    BGR8 = "bgr8"
    RGBA8 = "rgba8"
    BGRA8 = "bgra8"
    YUV422 = "yuv422"
    MJPEG = "mjpeg"
    DEPTH16 = "depth16"
    RAW8 = "raw8"
    RAW10 = "raw10"
    RAW12 = "raw12"
    RAW16 = "raw16"
    MOTION_XYZ32F = "motion_xyz32f"


@dataclass
class StreamProfile:
    format : StreamFormat


@dataclass
class VideoStreamProfile(StreamProfile):

    width : int
    height : int
    fps : int

    def __hash__(self):
        return hash((
            self.width, self.height,
            self.fps, self.format
            ))


# TODO: add more implementations for other stream types