from dataclasses import dataclass
from .environment import Environment, EnvironmentOptions
import pyrealsense2 as rs

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler()]
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineOptions:

    max_len_captured_data_buffer : int
    """
    For scalibility we keep the captured RGB/depth data inside a buffer, then process them.
    Since this buffer may cause a memory overhead, we allow you to set its maximum size.
    If maximum length is exceeded, capturing process will be suspended until any of older data is dequeued.
    """

        
class Pipeline:
    """
    The main pipeline for EyeBin project that organizes tasks.
    """

    def __init__(self,
                 environment : Environment,
                 options : PipelineOptions
                 ):
        self.opts = options
        self.env = environment


    def start_component_pipelines(self):
        """
        Starts RealSense's camera pipelines.
        """
        env = self.env

        if self.opts.optimized_startup:
            env.optimize_low_stereo_temperature() # heat sensors before proceeding

        config = rs.config()

        pipeline_rs = rs.pipeline()
        pass

        # TODO


    def capture(self):
        raise NotImplementedError()


    def start(self):
        """
        Starts the pipeline.
        """

        env = self.env
        
        env.init_components() # initialize the components

        self.start_component_pipelines()

        while self.all_components_healthy():
            pass

        # TODO