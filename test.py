from pipeline import Pipeline, PipelineOptions
from stream import VideoStreamProfile, StreamFormat

import numpy


ppl = Pipeline(PipelineOptions(
    # no options for now
))

sp_depth = VideoStreamProfile(
    format=StreamFormat.DEPTH16,
    width=1280,
    height=720,
    fps=30
    ) # define a stream profile of your choice

ppl.add_config(
    profiles={ sp_depth }
) # pass it to the configuration

ppl.start() # start receiving data

while ppl.alive():

    data : numpy.NDArray = ppl.stream(sp_depth).get()

    # do something