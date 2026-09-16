from comcam.util.formatter.impl.realsense import RSFormatter
from comcam.stream.profile import StreamFormat
from pyrealsense2 import format

import numpy as np

result = RSFormatter.convert_to(np.array([]), format.rgb8, StreamFormat.RGB8)