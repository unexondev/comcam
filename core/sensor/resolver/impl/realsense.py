from eyebin.core.sensor.impl.realsense import RSSensor, RSSensorOptions
from eyebin.core.sensor.resolver import SPResolver
from eyebin.stream.profile import StreamProfile

from pyrealsense2 import context as rs_context


class RSSPResolver(SPResolver):

    def __init__(self,
                 sensor_options : RSSensorOptions,
                 context : rs_context
                 ):

        super().__init__(sensor_options=sensor_options)

        # Realsense API provides context, store it
        self._ctx = context


    def resolve(self, stream_profile : StreamProfile) -> RSSensor | None:

        ctx = self._ctx

        # find devices supporting the given profile
        sensors = ctx.query_all_sensors()
        for sensor in sensors:

            rs_prfs_stream = sensor.get_stream_profiles()
            for rs_prf_stream in rs_prfs_stream:
                if stream_profile.matches(rs_prf_stream):
                    # create Sensor (RSSensor) instance
                    return RSSensor(
                        sensor=sensor,
                        options=self.opts_sensor
                        )
                
        return None