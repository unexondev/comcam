from pyrealsense2 import stream_profile as rs2_stream_profile
from pyrealsense2 import video_stream_profile as rs2_video_stream_profile
from comcam.stream.profile import StreamProfile, VideoStreamProfile


def is_profile_matching(sp : StreamProfile, sp_impl : rs2_stream_profile) -> bool:

    if isinstance(sp, VideoStreamProfile):

        if not sp_impl.is_video_stream_profile(): 
            return False

        sp_impl : rs2_video_stream_profile = sp_impl.as_video_stream_profile()

        # format is already being transformed
        return (sp.width == sp_impl.width() and
                sp.height == sp_impl.height() and
                sp.fps == sp_impl.fps()) 

    elif ...:
        raise NotImplementedError() # TODO