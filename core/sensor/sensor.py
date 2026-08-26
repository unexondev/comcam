from dataclasses import dataclass
from enum import Enum
from threading import Lock # for thread-safe

from eyebin.stream import Stream, StreamProfile


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

        # initialize an empty set for stream profiles
        self._profiles : set[StreamProfile] = set()

        # define receiver stream
        self._stream : Stream | None = None

        # create mutex
        self._lock = Lock()


    @property
    def state(self):
        return self._state


    @property
    def options(self):
        return self.opts


    @property
    def profiles(self):
        return self._profiles.copy()


    """
    Sensor Management APIs
    """

    def configure(self, stream : Stream, stream_profiles : set[StreamProfile]):
        """
        Configure the sensor so it can then stream on
        given stream configuration after the next time it's opened.
        
        Args:
            stream: A `Stream` object where sensor pushes captured data.
            stream_profiles: A set of `StreamProfile` objects that defines how sensor will produce data.
        """
        self._profiles = stream_profiles.copy()
        self._stream = stream


    def open(self):
        """
        Open the sensor physically.

        Raises:
            SensorOpenError: If sensor couldn't be opened successfully.
        """
        with self._lock:
            self._state = SensorState.OPENED


    def close(self):
        """
        Close the sensor physically.

        Raises:
            SensorCloseError: If sensor couldn't be closed successfully.
        """
        with self.lock:
            self._state = SensorState.CLOSED


    def start(self):
        """
        Start the sensor (start streaming) physically.

        Raises:
            SensorStartError: If sensor couldn't be started successfully.
        """
        with self._lock:
            self._state = SensorState.STREAMING


    def stop(self):
        """
        Stop the sensor (end streaming) physically.

        Raises:
            SensorStopError: If sensor couldn't be stopped successfully.
        """
        with self._lock:
            self._state = SensorState.OPENED


    """
    Sensor Information Query APIs
    """

    def is_opened(self):
        """
        Check if sensor is physically in `Opened` state.

        Raises:
            SensorInfoError: If an error occurs while gathering the sensor information.
        """
        raise NotImplementedError()


    def is_closed(self):
        """
        Check if sensor is physically in `Closed` state.

        Raises:
            SensorInfoError: If an error occurs while gathering the sensor information.
        """
        return not self.is_opened()


    def is_healthy(self):
        """
        Check if sensor is healthy under constraints passed in `options`.

        Raises:
            SensorInfoError: If an error occurs while gathering the sensor information.
        """
        raise NotImplementedError()


    """
    Private Functions
    """

    def _fail(self):
        with self._lock:
            self._state = SensorState.ERRORED
        