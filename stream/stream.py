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

        self._cond = Condition() # for thread-safe push/pops


    def push(self, data : NDArray):
        """
        Pushes data to the stream.

        Args:
            data: An `NDArray` to push to the queue.
        """
        with self._cond:
            self._queue.append(data)
            self._cond.notify()


    def popleft(self) -> NDArray:
        """
        Pops data from the stream (left).

        Returns:
            An NDArray popped from the stream.
        """
        with self._cond:
            return self._queue.popleft()


    def pop(self) -> NDArray:
        """
        Pops data from the stream.

        Returns:
            An NDArray popped from the stream.
        """
        with self._cond:
            return self._queue.pop()


    def wait_left(self, until_ms : int = 5000) -> NDArray:
        """
        TODO docstring & timestamp evalulation
        """

        with self._cond:

            while not self._queue:
                self._cond.wait()

            return self._queue.popleft()


    def wait(self, until_ms : int = 5000) -> NDArray:
        """
        TODO docstring & timestamp evalulation
        """

        with self._cond:

            while not self._queue:
                self._cond.wait()

            return self._queue.pop()