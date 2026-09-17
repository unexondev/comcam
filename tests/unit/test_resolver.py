from comcam.util.resolver import SensorResolver
from comcam.util.resolver.resolver import SensorResolverInterface
from comcam.stream import VideoStreamProfile, StreamFormat, StreamType


def test_custom_resolver():

    class FakeSensor:
        pass

    sensor_rgb8, sensor_rgba8 = FakeSensor(), FakeSensor()

    class FakeResolver(SensorResolverInterface):

        @classmethod
        def resolve(cls, stream_profile):

            if not isinstance(stream_profile, VideoStreamProfile):
                return

            if stream_profile.format == StreamFormat.RGB8:
                yield sensor_rgb8

            elif stream_profile.format == StreamFormat.RGBA8:
                yield sensor_rgba8

    SensorResolver.register("test", FakeResolver)

    vsp_rgb8 = VideoStreamProfile(
                    stream_type=StreamType.COLOR,
                    format=StreamFormat.RGB8,
                    width=1920,
                    height=1080,
                    fps=60
                    )
    vsp_rgba8 = VideoStreamProfile(
                    stream_type=StreamType.COLOR,
                    format=StreamFormat.RGBA8,
                    width=600,
                    height=400,
                    fps=30
                    )

    # with api name is given
    assert next(SensorResolver.resolve(vsp_rgb8, api_name="test")) == sensor_rgb8
    # without api name is given
    assert next(SensorResolver.resolve(vsp_rgba8)) == sensor_rgba8