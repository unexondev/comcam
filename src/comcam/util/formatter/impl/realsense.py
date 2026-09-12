from collections import defaultdict

from ..formatter import *

from comcam.stream.profile import StreamFormat

# Realsense API
from pyrealsense2 import format as rs2_format


_ALIAS = Formatter._convert_alias


class RSFormatter(Formatter):

    converters = defaultdict(dict, {

        rs2_format.z16: {StreamFormat.DEPTH16: _ALIAS},

        rs2_format.disparity16: {StreamFormat.DISPARITY16: _ALIAS},

        rs2_format.xyz32f: {StreamFormat.MOTION_XYZ32F: _ALIAS},

        rs2_format.yuyv: {StreamFormat.YUYV: _ALIAS},

        rs2_format.rgb8: {StreamFormat.RGB8: _ALIAS},

        rs2_format.bgr8: {StreamFormat.BGR8: _ALIAS},

        rs2_format.rgba8: {StreamFormat.RGBA8: _ALIAS},

        rs2_format.bgra8: {StreamFormat.BGRA8: _ALIAS},

        rs2_format.y8: {StreamFormat.GRAY8: _ALIAS},

        rs2_format.y16: {StreamFormat.GRAY16: _ALIAS},

        rs2_format.raw10: {StreamFormat.RAW10: _ALIAS},

        rs2_format.raw16: {StreamFormat.RAW16: _ALIAS},

        rs2_format.raw8: {StreamFormat.RAW8: _ALIAS},

        rs2_format.uyvy: {StreamFormat.UYVY: _ALIAS},

        rs2_format.motion_raw: {StreamFormat.MOTION_RAW: _ALIAS},

        rs2_format.motion_xyz32f: {StreamFormat.MOTION_XYZ32F: _ALIAS},

        rs2_format.gpio_raw: {StreamFormat.GPIO_RAW: _ALIAS},

        rs2_format.six_dof: {StreamFormat.SIX_DOF: _ALIAS},

        rs2_format.disparity32: {StreamFormat.DISPARITY32: _ALIAS},

        rs2_format.y10bpack: {StreamFormat.Y10BPACK: _ALIAS},

        rs2_format.distance: {StreamFormat.DEPTH16: _ALIAS},

        rs2_format.mjpeg: {StreamFormat.MJPEG: _ALIAS},

        rs2_format.y8i: {StreamFormat.Y8I: _ALIAS},

        rs2_format.y12i: {StreamFormat.Y12I: _ALIAS},

        rs2_format.inzi: {StreamFormat.INZI: _ALIAS},

        rs2_format.invi: {StreamFormat.INVI: _ALIAS},

        rs2_format.w10: {StreamFormat.RAW10: _ALIAS},

        rs2_format.fg: {StreamFormat.FG: _ALIAS},

        rs2_format.y411: {StreamFormat.YUV411: _ALIAS},

        rs2_format.y16i: {StreamFormat.Y16I: _ALIAS},

        rs2_format.m420: {StreamFormat.YUV420: _ALIAS},

        rs2_format.combined_motion: {StreamFormat.COMBINED_MOTION: _ALIAS},

        rs2_format.nv12: {StreamFormat.NV12: _ALIAS},

        # TODO define converters between them

    })

    @classmethod
    def convertible(cls,
                    source_format : rs2_format,
                    destination_format : StreamFormat
                    ):
        # just for type hinting
        return super().convertible(source_format, destination_format)


    @classmethod
    def convert(cls,
                source_data : NDArray,
                source_format : rs2_format,
                destination_format : StreamFormat
                ) -> NDArray:

        return super().convert(source_data, source_format, destination_format)