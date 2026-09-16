from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto


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
    YUYV = "yuyv"
    UYVY = "yuyv"
    YVYU = "yuyv"
    VYUY = "yuyv"
    YUV411 = "yuv411"
    YUV420 = "yuv420"
    MJPEG = "mjpeg"
    DEPTH16 = "depth16"
    RAW8 = "raw8"
    RAW10 = "raw10"
    RAW12 = "raw12"
    RAW16 = "raw16"
    MOTION_XYZ32F = "motion_xyz32f"
    MOTION_RAW = "motion_raw"
    DISPARITY16 = "disparity16"
    DISPARITY32 = "disparity32"
    GPIO_RAW = "gpio_raw"
    SIX_DOF = "six_dof"
    Y10BPACK = "y10bpack"
    Y8I = "y8i"
    Y12I = "y12i"
    Y16I = "y16i"
    FG = "fg"
    COMBINED_MOTION = "combined_motion"
    INZI = "INZI"
    INVI = "INVI"
    NV12 = "NV12"


class StreamType(Enum):
    COLOR = "color"
    DEPTH = "depth"
    INFRARED = "infrared"
    FISHEYE = "fisheye"
    MOTION = "motion"
    GYRO = "gyro"
    ACCEL = "accel"
    CONFIDENCE = "confidence"
    POSE = "pose"


@dataclass(frozen=True)
class StreamProfile:
    stream_type : StreamType
    format : StreamFormat | None
    fps : int

    def unformatted(self):
        return replace(self, format=None)

    def get_frame(self):
        raise NotImplementedError()


@dataclass(frozen=True)
class VideoFrame:
    width : int
    height : int


@dataclass(frozen=True)
class VideoStreamProfile(StreamProfile, VideoFrame):

    def get_frame(self):
        return VideoFrame(
            width=self.width,
            height=self.height
            )


VIDEO_STREAMS = [
    StreamType.COLOR,
    StreamType.DEPTH,
    StreamType.INFRARED,
    StreamType.FISHEYE,
    StreamType.CONFIDENCE
]

# TODO: add more implementations for other stream types