import pytest

from comcam.pipeline import Pipeline, PipelineOptions
from comcam.core.sensor import Sensor, DeviceDesc, SensorOptions, SensorState
from comcam.stream import VideoStreamProfile, StreamFormat, StreamType

class FakeSensor(Sensor):

    n_instance = 0

    def __init__(self):
        mock_desc = DeviceDesc(
            product_name="product name (mock index: %d)" % FakeSensor.n_instance,
            serial_number="serial number (mock index: %d)" % FakeSensor.n_instance
            )
        mock_opts = SensorOptions()
        super().__init__(mock_desc, mock_opts)
        FakeSensor.n_instance += 1

    def __hash__(self):
        return hash(( self.device ))

    def __eq__(self, other):
        if not isinstance(other, FakeSensor):
            return NotImplemented
        return (self.device.product_name == other.device.product_name and
                self.device.serial_number == other.device.serial_number)


def test_common_flow():

    ppl = Pipeline(PipelineOptions())
    # assert pipeline is not alive before it's started
    assert not ppl.alive()

    sensor_mock = FakeSensor()
    vsp = VideoStreamProfile(
        stream_type=StreamType.COLOR,
        format=StreamFormat.RAW8,
        width=1920,
        height=1080,
        fps=60
        )

    ppl.create_stream(vsp, sensor=sensor_mock)

    sensor = ppl.get_sensor(vsp)

    assert sensor == sensor_mock

    ppl.start()

    assert ppl.alive()
    assert ppl.alive(sensor)

    assert sensor_mock.state == SensorState.STREAMING

    assert ppl.stream(vsp) is not None

    ppl.stop()

    assert sensor_mock.state == SensorState.CLOSED


def test_dupl_config():

    ppl = Pipeline(PipelineOptions())

    sensor_mock_old = FakeSensor()
    sensor_mock_repl = FakeSensor()
    vsp = VideoStreamProfile(
        stream_type=StreamType.COLOR,
        format=StreamFormat.RAW8,
        width=1920,
        height=1080,
        fps=60
        )

    ppl.create_stream(vsp, sensor=sensor_mock_old)
    ppl.create_stream(vsp, sensor=sensor_mock_old)

    assert len(sensor_mock_old.config.profiles()) == 1

    ppl.create_stream(vsp, sensor=sensor_mock_repl)

    assert ppl.get_sensor(vsp) == sensor_mock_repl

    assert len(sensor_mock_repl.config.profiles()) == 1


def test_with_auto_resolve():

    class FakeResolver:

        def __init__(self, sensors : list[Sensor]):
            self.iter_sensors = iter(sensors)

        def resolve(self, stream_profile):
            yield from self.iter_sensors

    ppl = Pipeline(
        PipelineOptions(),
        resolver=FakeResolver([ FakeSensor() ])
        )

    vsp = VideoStreamProfile(
        stream_type=StreamType.COLOR,
        format=StreamFormat.RAW8,
        width=1920,
        height=1080,
        fps=60
        )

    with pytest.raises(RuntimeError):
        ppl.start()

    ppl.create_stream(vsp)

    ppl.start()

    assert ppl.alive()


def test_pipeline_sensor_scope():

    class FakeResolver:

        def __init__(self, sensors : list[Sensor]):
            self.iter_sensors = iter(sensors)

        def resolve(self, stream_profile):
            yield from self.iter_sensors

    sensor_0, vsp_0 = FakeSensor(), VideoStreamProfile(
                                        stream_type=StreamType.COLOR,
                                        format=StreamFormat.RAW8,
                                        width=1920,
                                        height=1080,
                                        fps=60
                                        )
    sensor_1, vsp_1 = FakeSensor(), VideoStreamProfile(
                                        stream_type=StreamType.COLOR,
                                        format=StreamFormat.RAW8,
                                        width=1920,
                                        height=1080,
                                        fps=30
                                        )
    sensor_2, vsp_2 = FakeSensor(), VideoStreamProfile(
                                        stream_type=StreamType.COLOR,
                                        format=StreamFormat.RAW8,
                                        width=1920,
                                        height=1080,
                                        fps=6
                                        )

    ppl = Pipeline(
        PipelineOptions(),
        resolver=FakeResolver([ sensor_0, sensor_1, sensor_2 ])
        )

    ppl.create_stream(vsp_0, sensor_0)
    ppl.create_stream(vsp_1, sensor_1)
    ppl.create_stream(vsp_2, sensor_2)

    ppl.start(sensor_0)

    assert not ppl.alive() # rest of streams must be alive too
    assert ppl.alive(sensor_0)

    ppl.start(sensor_1)

    assert ppl.alive(sensor_0) and ppl.alive(sensor_1)
    assert not ppl.alive(sensor_2)

    ppl.start(sensor_2)

    assert ppl.alive() # now must be alive since all sensors are open

    ppl.stop(sensor_0)

    assert not ppl.alive()
    assert not ppl.alive(sensor_0)

    ppl.stop(sensor_1)
    ppl.stop(sensor_2)
    with pytest.raises(RuntimeError):
        ppl.stop(sensor_0) # already stopped

    assert not ppl.alive()


def test_stream_supported_by_multiple_sensors():
    """
    Let's see if it works properly if given stream
    profile is supported by different sensors.
    """

    class FakeResolver:

        def __init__(self, sensors : list[Sensor]):
            self.sensors = sensors

        def resolve(self, stream_profile):
            # iterates from beginning every call
            yield from self.sensors

    sensor_0 = FakeSensor()
    sensor_1 = FakeSensor()

    vsp = VideoStreamProfile(
            stream_type=StreamType.COLOR,
            format=StreamFormat.RAW8,
            width=1920,
            height=1080,
            fps=60
            )

    ppl = Pipeline(
        PipelineOptions(),
        resolver=FakeResolver([ sensor_0, sensor_1 ])
        )

    ppl.create_stream(vsp)

    assert ppl.get_sensor(vsp) == sensor_0

    ppl.create_stream(vsp)

    assert ppl.get_sensor(vsp) == sensor_0

    ppl.remove_stream(vsp)

    with pytest.raises(KeyError):
        ppl.stream(vsp)

    stream = ppl.create_stream(vsp, sensor_1)

    assert ppl.stream(vsp) == stream

    ppl.start()

    assert ppl.alive()


def test_sensor_streams_multiple_profiles():
    """
    Let's see if it works properly if different stream
    profiles are streamed by single sensor.
    """

    class FakeResolver:

        def __init__(self, sensors : list[Sensor]):
            self.sensors = sensors

        def resolve(self, stream_profile):
            # iterates from beginning every call
            yield from self.sensors

    sensor = FakeSensor()

    vsp_0 = VideoStreamProfile(
                stream_type=StreamType.COLOR,
                format=StreamFormat.RAW8,
                width=1920,
                height=1080,
                fps=60
                )
    vsp_1 = VideoStreamProfile(
                stream_type=StreamType.COLOR,
                format=StreamFormat.RAW8,
                width=600,
                height=400,
                fps=30
                )

    ppl = Pipeline(
        PipelineOptions(),
        resolver=FakeResolver([ sensor ])
        )

    stream_0 = ppl.create_stream(vsp_0)
    stream_1 = ppl.create_stream(vsp_1)

    assert stream_0 is not stream_1

    assert ppl.get_sensor(vsp_0) == ppl.get_sensor(vsp_1) == sensor

    ppl.start()

    assert ppl.alive()