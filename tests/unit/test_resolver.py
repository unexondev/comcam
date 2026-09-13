from comcam.util.resolver import SensorResolver
from comcam.stream import VideoStreamProfile, StreamFormat


def test_custom_resolver():

    class FakeSensor:
        pass

    sensor_rgb8, sensor_rgba8 = FakeSensor(), FakeSensor()

    def resolve(stream_profile):

        if not isinstance(stream_profile, VideoStreamProfile):
            return

        if stream_profile.format == StreamFormat.RGB8:
            yield sensor_rgb8

        elif stream_profile.format == StreamFormat.RGBA8:
            yield sensor_rgba8

    SensorResolver.register("test", resolve)

    vsp_rgb8 = VideoStreamProfile(StreamFormat.RGB8, 1920, 1080, 60)
    vsp_rgba8 = VideoStreamProfile(StreamFormat.RGBA8, 600, 400, 30)

    assert next(SensorResolver.resolve(vsp_rgb8)) == sensor_rgb8
    assert next(SensorResolver.resolve(vsp_rgba8)) == sensor_rgba8