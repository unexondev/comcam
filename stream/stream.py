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


    def put(self, data : NDArray):
        """
        Puts new data to the stream.

        Args:
            data: An `NDArray` to push to the queue.
        """
        with self._cond:
            self._queue.append(data)
            self._cond.notify()


    def _wait(self, timeout_ms):

        init_ms = time.monotonic_ns() // 1_000_000

        while not self._queue:

            cur_ms = time.monotonic_ns() // 1_000_000
            wait_ms = timeout_ms - (cur_ms - init_ms)

            if wait_ms <= 0:
                return False

            self._cond.wait(timeout=wait_ms)

        return True


    def wait_oldest(self, timeout_ms : int = 5000) -> NDArray | None:
        """
        Pops oldest data from stream or waits for new data to be arrived.
        
        Args:
            until_ms: An `int` represents the time to wait before returning as milliseconds.

        Returns:
            Popped `NDArray` if any data exist or arrived within `until_ms`, `None` otherwise.
        """

        with self._cond:

            if not self._wait(timeout_ms):
                return None

            return self._queue.popleft()


    def wait_recent(self, timeout_ms : int = 5000) -> NDArray:
        """
        Pops recent data from stream or waits for new data to be arrived.
        
        Args:
            until_ms: An `int` represents the time to wait before returning as milliseconds.

        Returns:
            Popped `NDArray` if any data exist or arrived within `until_ms`, `None` otherwise.
        """

        with self._cond:

            if not self._wait(timeout_ms):
                return None

            return self._queue.pop()