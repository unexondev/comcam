from ..lifter import ProfileLifter
from comcam.stream.profile import (
    StreamProfile, StreamType,
    StreamFormat, VideoStreamProfile
    )

from pyrealsense2 import stream_profile as rs2_stream_profile
from pyrealsense2 import stream as rs2_stream

class RSProfileLifter(ProfileLifter):

    stream_type_map = {
        rs2_stream.color: StreamType.COLOR,
        rs2_stream.depth: StreamType.DEPTH,
        rs2_stream.infrared: StreamType.INFRARED,
        rs2_stream.fisheye: StreamType.FISHEYE,
        rs2_stream.motion: StreamType.MOTION,
        rs2_stream.gyro: StreamType.GYRO,
        rs2_stream.accel: StreamType.ACCEL,
        rs2_stream.confidence: StreamType.CONFIDENCE,
        rs2_stream.pose: StreamType.POSE
    }

    @classmethod
    def lift(cls, backend_profile : rs2_stream_profile) -> StreamProfile:

        ty_backend = backend_profile.stream_type()

        ty_stream = cls.stream_type_map.get(ty_backend)

        if ty_stream is None:

            raise NotImplementedError("Stream type %r is not supported." % ty_backend)

        if backend_profile.is_video_stream_profile():

            backend_profile = backend_profile.as_video_stream_profile()

            return VideoStreamProfile(
                stream_type=ty_stream,
                format=None, # unformatted
                fps=backend_profile.fps(),
                width=backend_profile.width(),
                height=backend_profile.height()
                )

        else:
            raise NotImplementedError("Only video stream profiles are supported for now.")