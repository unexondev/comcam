from pipeline import Pipeline, PipelineOptions
from stream import VideoStreamProfile, StreamFormat

pipe = Pipeline(PipelineOptions(
    # no options for now
))

sp_depth = VideoStreamProfile(StreamFormat.DEPTH16, 1280, 720, 30)

pipe.add_config(
    profiles={ sp_depth }
)

pipe.start() # start pipeline