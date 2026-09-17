from collections.abc import Iterator

from ..resolver import SensorResolverInterface

from comcam.core.sensor import DeviceDesc
from comcam.core.sensor.impl.realsense import RSSensor, RSSensorOptions
from comcam.stream.profile import StreamProfile

from pyrealsense2 import context as rs_context
from pyrealsense2 import camera_info as rs_camera_info


class RSSensorResolver(SensorResolverInterface):

    @classmethod
    def resolve(cls, stream_profile):

        for sensor in cls.resolve_all():
            
            if stream_profile in sensor.supported_stream_profiles():

                yield sensor


    @classmethod
    def resolve_all(cls):

        ctx = rs_context() # context is required

        devices = ctx.query_devices()
        for device in devices:

            for sensor in device.sensors:

                desc = DeviceDesc(
                    product_name=device.get_info(rs_camera_info.name),
                    serial_number=sensor.get_info(rs_camera_info.serial_number)
                )

                yield RSSensor(
                    sensor=sensor,
                    device_desc=desc,
                    options=RSSensorOptions()
                    ) # yield sensor


# Register Realsense resolver
from comcam.util.resolver import SensorResolver
SensorResolver.register("RealSense", resolver=RSSensorResolver)