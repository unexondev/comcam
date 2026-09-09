# ComCam - The Common Camera API
_ComCam is a common API for different camera APIs_. Without having to know how vendors provide an interface to access your cameras, you can easily interact with them using a single, basic and abstracted programming interface.

## Example Usage
```py
from pipeline import Pipeline, PipelineOptions
from stream import VideoStreamProfile, StreamFormat

import numpy


ppl = Pipeline(
    PipelineOptions(
        # no options for now
    )
) # initialize the pipeline

sp_depth = VideoStreamProfile(
    format = StreamFormat.DEPTH16,
    width = 1280,
    height = 720,
    fps = 30
) # define a stream profile of your choice

ppl.add_config(
    profiles = {
        sp_depth
    }
) # pass it to the configuration

ppl.start() # start receiving data

while ppl.alive():

    data : numpy.NDArray = ppl.stream(sp_depth).get()

    ... # whatever
```

## Installation


## Supported vendor APIs
For now, we support:
- **Realsense 2 SDK**

> Note: ComCam is almost a new project. Other vendor APIs will be added in order.