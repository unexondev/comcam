from collections import deque
from threading import Condition
import time

from numpy.typing import NDArray

import logging

logger = logging.getLogger(__name__)



class Stream:
    """
    TODO add docstring
    """

    def __init__(self):
        self._queue : deque[NDArray] = deque()


    def push(self, data : NDArray):
        """
        Pushes data to the stream.

        Args:
            data: An `NDArray` to push to the queue.
        """
        self._queue.append(data)


    """
    TODO: Check threading.Condition ***
    """