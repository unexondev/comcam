from __future__ import annotations
from types import MappingProxyType
from typing import Iterator

from comcam.stream.profile import StreamProfile, VideoStreamProfile
from comcam.stream.stream import Stream


class PublicConfigMixin:

    _stream_map : dict[StreamProfile, Stream]

    def get_stream(self, stream_profile : StreamProfile) -> Stream:
        return self._stream_map[stream_profile]


    def profiles_iter(self) -> Iterator[StreamProfile]:
        return iter(self._stream_map)


    def profiles(self):
        return list(self._stream_map)


    def is_empty(self) -> bool:
        return not self._stream_map


    def __iter__(self):
        return iter(self._stream_map.items())


class SensorConfig(PublicConfigMixin):

    def __init__(self, stream_map : dict[StreamProfile, Stream] = None):

        # initialize the stream map
        self._stream_map = {} if stream_map is None else stream_map


    def use(self, stream_profile : StreamProfile, stream : Stream = None) -> None:

        for vsp_other in self:

            if stream_profile.get_frame() == vsp_other.get_frame():
                # duplicate frame (differing by frame rate and format)
                raise RuntimeError("Video stream profiles represent same frame are not allowed.")
    
        self._stream_map[stream_profile] = stream


    def remove(self, stream_profile : StreamProfile) -> None:
        del self._stream_map[stream_profile]


    def clear(self) -> None:
        self._stream_map.clear()


    def copy(self) -> SensorConfig:
        return SensorConfig(self._stream_map.copy())


    def view(self) -> SensorConfigView:
        return SensorConfigView(self)


class SensorConfigView(PublicConfigMixin):

    def __init__(self, sensor_config : SensorConfig):

        self._stream_map = MappingProxyType(sensor_config._stream_map)