from collections.abc import Iterator

# import Realsense formatter
from comcam.util.formatter.impl.realsense import RSFormatter

from comcam.core.sensor import DeviceDesc
from comcam.core.sensor.impl.realsense import RSSensor, RSSensorOptions
from comcam.stream.profile import StreamProfile
from comcam.stream.profile.lifter.impl.realsense import RSProfileLifter

from pyrealsense2 import context as rs_context
from pyrealsense2 import camera_info as rs_camera_info


def resolve_realsense2(stream_profile : StreamProfile) -> Iterator[ RSSensor ]:

    ctx = rs_context() # context is required

    devices = ctx.query_devices()
    for device in devices:

        for sensor in device.sensors:

            profiles_supported = sensor.get_stream_profiles()
            for profile_supported in profiles_supported:

                if RSSensor.rs_profile_matches(profile_supported, stream_profile):

                    desc = DeviceDesc(
                        product_name=device.get_info(rs_camera_info.name),
                        serial_number=sensor.get_info(rs_camera_info.serial_number)
                    )

                    yield RSSensor(
                        sensor=sensor,
                        device_desc=desc,
                        options=RSSensorOptions()
                        ) # yield sensor
                

# Register Realsense SDK
from comcam.util.resolver import SensorResolver
SensorResolver.register("RealSense", resolver=resolve_realsense2)