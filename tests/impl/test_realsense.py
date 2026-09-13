import pytest
from comcam.pipeline import Pipeline, PipelineOptions
from comcam.stream import VideoStreamProfile, StreamFormat
from comcam.util.formatter.impl.realsense import RSFormatter

from pyrealsense2 import context as rs2_context
from pyrealsense2 import video_stream_profile as rs2_video_stream_profile


@pytest.fixture
def context():

    ctx = rs2_context()
    if not ctx.sensors:
        pytest.skip("No Realsense sensor is detected.")

    return ctx


@pytest.fixture
def stream_profiles_by_same_sensor(context : rs2_context):

    for sensor in context.sensors:

        vsps = []

        for profile in sensor.profiles:
            if not profile.is_video_stream_profile():
                continue
            profile : rs2_video_stream_profile = profile.as_video_stream_profile()
            for fmt in StreamFormat:
                if RSFormatter.convertible(profile.format(), fmt):
                    vsps.append(VideoStreamProfile(
                        format=fmt,
                        width=profile.width(), 
                        height=profile.height(),
                        fps=profile.fps()
                    ))
                    break

        if len(vsps) > 1:
            return (sensor, vsps)

    pytest.skip("No sensor with multiple video stream profile support could be found.")


def test_pipeline(stream_profiles_by_same_sensor):
    """
    Integration test covering a complete real-world pipeline scenario.
    """

    ppl = Pipeline(
        PipelineOptions()
        )

    sensor, vsps = stream_profiles_by_same_sensor

    stream_0 = ppl.create_stream(vsps[0], sensor)
    stream_1 = ppl.create_stream(vsps[1], sensor)

    assert stream_0 is not stream_1

    ppl.start()

    assert ppl.alive()

    data_0 = stream_0.wait(2500) # 2.5 seconds for each

    assert data_0 is not None

    data_1 = stream_1.wait(2500)

    assert data_1 is not None

    ppl.stop()