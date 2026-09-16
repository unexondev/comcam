import pytest

from comcam.pipeline import Pipeline, PipelineOptions
from comcam.stream import StreamProfile
from comcam.stream.profile.lifter.impl.realsense import RSProfileLifter
from comcam.util.formatter.impl.realsense import RSFormatter

from pyrealsense2 import context as rs2_context


@pytest.fixture
def context() -> rs2_context:

    ctx = rs2_context()
    if not ctx.sensors:
        pytest.skip("No Realsense sensor is detected.")

    return ctx


@pytest.fixture
def sensor_with_multiple_profiles(context : rs2_context):

    for sensor in context.sensors:

        stream_profiles : set[StreamProfile] = set()

        for prf_sensor in sensor.profiles:

            prf_stream = None
            try:
                prf_stream = RSProfileLifter.lift(prf_sensor)
            except NotImplementedError:
                continue

            if not RSFormatter.convertible(prf_sensor.format()):
                continue

            cvts = RSFormatter.get_converters(prf_sensor)

            fmt_to, converter = next(iter(cvts))

            prf_stream.format = fmt_to # set format

            if any(prf_stream.get_frame() == sp_saved.get_frame() for sp_saved in stream_profiles):
                # we already have equivalent, skip it.
                continue

            stream_profiles.add(prf_stream)

        if len(stream_profiles) > 1:

            return (sensor, stream_profiles)

    pytest.skip("No sensors supporting multiple stream profiles.")


def test_multi_stream_pipeline(sensor_with_multiple_profiles):
    """
    Integration test covering multiple stream
    profiles are being produced by the same sensor.
    """

    ppl = Pipeline(
        PipelineOptions()
        )

    sensor, stream_profiles = sensor_with_multiple_profiles

    stream_0 = ppl.create_stream(stream_profiles[0], sensor)
    stream_1 = ppl.create_stream(stream_profiles[1], sensor)

    assert stream_0 is not stream_1

    ppl.start()

    assert ppl.alive()

    data_0 = stream_0.wait(2500) # 2.5 seconds for each

    assert data_0 is not None

    data_1 = stream_1.wait(2500)

    assert data_1 is not None

    ppl.stop()