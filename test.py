from eyebin import create_context
from eyebin import Environment, EnvironmentOptions
from eyebin import Stream, StreamOptions
from eyebin import VideoStreamProfile, StreamType, StreamFormat

import numpy
import cv2
import time


# get the context first
context = create_context()

# create stream profiles
sp_depth = VideoStreamProfile(StreamType.depth, StreamFormat.z16, 1280, 720, 30)
sp_color = VideoStreamProfile(StreamType.color, StreamFormat.rgba8, 1280, 720, 30)

# set enviornment options
opts_env = EnvironmentOptions(
    optimized_startup=False,
    asic_temp_range_stereo=(30.0, 40.0),
    projector_temp_range_stereo=(27.0, 40.0)
)

# create environment for the stream profiles requested
env = Environment.create(context, { sp_depth, sp_color }, opts_env)

# set stream options
opts_stream = StreamOptions()

# create stream
stream = Stream.create(env, opts_stream)

# start the stream
stream.start()

img = None

# stream is consumable while it's active
while stream.active():

    frameset = stream.get_data()

    if frameset is None:
        continue

    fcolor = frameset.get_color_frame() 

    img = numpy.asanyarray(fcolor.get_data())
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    

    cv2.imshow("COLOR", img)

    if cv2.waitKey(1) == 27:   # ESC
        break

# stop stream
stream.stop()

# close all windows
cv2.destroyAllWindows()