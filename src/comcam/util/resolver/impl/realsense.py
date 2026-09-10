from __future__ import annotations

from comcam.core.sensor.impl.realsense import RSSensor
from comcam.stream.profile import StreamProfile
from comcam.util.profile.impl.realsense import is_profile_matching

from pyrealsense2 import context as rs_context
from pyrealsense2 import camera_info as rs_camera_info

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..descs import PVID


def resolve(stream_profile : StreamProfile,
            pvid : PVID | None = None
            ) -> RSSensor | None:

    ctx = rs_context() # context is required

    devices = ctx.query_devices()
    for device in devices:

        if pvid is not None:

            pid_str = device.get_info(rs_camera_info.product_id)
            pid = int(pid_str, base=16)

            if pid != pvid.product_id:
                continue

        for sensor in device.sensors:

            rs_prfs_stream = sensor.get_stream_profiles()
            for rs_prf_stream in rs_prfs_stream:

                if is_profile_matching(stream_profile, rs_prf_stream):
                    # create Sensor (RSSensor) instance
                    return RSSensor(
                        sensor=sensor
                        )
                
    return None