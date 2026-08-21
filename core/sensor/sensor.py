from dataclasses import dataclass
from enum import Enum

from eyebin.stream.profile import StreamProfile


@dataclass
class SensorOptions:
    pass


class SensorState(Enum):
    CLOSED = 0,
    OPENED = 1,
    STREAMING = 2,
    ERRORED = 3


class Sensor:
    """
    Abstraction class for all types of sensors.

    This abstraction is responsible for physical implementation of sensors,
    higher level implementations are expected to depend on context. 

    Assumptions:
        - Sensors can physically have 3 states:
            - `Closed` state,
            - `Opened` state,
            - `Streaming` (or `Started`) state.

    The derived classes must implement the functions properly
    to ensure that all assumptions are satisfied.
    """
    def __init__(self, options : SensorOptions):
        # initialize state
        self._state = SensorState.CLOSED
        # store sensor options
        self.opts = options
        # Initialize an empty set for stream profiles
        self._profiles : set[StreamProfile] = set()

    @property
    def state(self):
        return self._state

    def configure(self, stream_profiles : set[StreamProfile]):
        """
        Configure the sensor so it can then stream on
        given stream profiles after the next time it's opened.
        """
        self._profiles = stream_profiles.copy()

    def open(self):
        """
        Open the sensor physically.

        Raises:
            SensorOpenError: If sensor couldn't be opened successfully.
        """
        self._state = SensorState.OPENED

    def close(self):
        """
        Close the sensor physically.

        Raises:
            SensorCloseError: If sensor couldn't be closed successfully.
        """
        self._state = SensorState.CLOSED

    def start(self):
        """
        Start the sensor (start streaming) physically.

        Raises:
            SensorStartError: If sensor couldn't be started successfully.
        """
        self._state = SensorState.STREAMING

    def stop(self):
        """
        Stop the sensor (end streaming) physically.

        Raises:
            SensorStopError: If sensor couldn't be stopped successfully.
        """
        self._state = SensorState.OPENED

    def is_opened(self):
        """
        Check if sensor is physically in `Opened` state.

        Raises:
            SensorStateError: If an error occured during retrieving the sensor state.
        """
        raise NotImplementedError()

    def is_closed(self):
        """
        Check if sensor is physically in `Closed` state.

        Raises:
            SensorStateError: If an error occured during retrieving the sensor state.
        """
        return not self.is_opened()

    def _fail(self):
        self._state = SensorState.ERRORED