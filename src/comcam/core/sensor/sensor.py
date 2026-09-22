from dataclasses import dataclass, replace

from enum import Enum
from threading import Lock # for thread-safe

from comcam.stream import Stream, StreamProfile
from .config import SensorConfig, SensorConfigView


@dataclass
class SensorOptions:
    pass


class SensorState(Enum):
    CLOSED = 0
    OPENED = 1
    STREAMING = 2
    ERRORED = 3


@dataclass(frozen=True)
class DeviceDesc:
    product_name: str | None
    serial_number: str | None


class Sensor:
    """
    Wrapper class for all types of sensors.

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
    def __init__(self,
                 device_desc : DeviceDesc,
                 options : SensorOptions,
                 config : SensorConfig | None = None
                 ):

        # initialize sensor descriptor
        self.device = device_desc

        # initialize state
        self._state = SensorState.CLOSED

        # save the config
        self.opts = options

        # define the config
        self._conf = SensorConfig() if config is None else config

        # create mutex
        self._lock = Lock()


    @property
    def state(self):
        with self._lock:
            return self._state


    @property
    def config(self) -> SensorConfig | SensorConfigView:
        """
        Don't mutate configuration after the sensor is opened,
        since this access returns SensorConfigView
        instead of SensorConfig after that.
        """
        with self._lock:
            if self._state == SensorState.CLOSED:
                return self._conf
            else:
                return self._conf.view()


    """
    Identity functions
    """

    def __hash__(self):
        raise NotImplementedError(
            "Since sensors can be derived from same devices, "
            "this function must be implemented by subclasses.")

    def __eq__(self, other):
        raise NotImplementedError(
            "Since sensors can be derived from same devices, "
            "this function must be implemented by subclasses.")


    """
    Sensor Management APIs
    """

    def supported_stream_profiles(self) -> set[StreamProfile]:
        """
        Get supported stream profiles by the sensor.

        Returns:
            A list of `StreamProfile` instances supported.
        """
        raise NotImplementedError()

    def open(self):
        """
        Open the sensor physically.

        Raises:
            SensorOpenError: If sensor couldn't be opened successfully.
        """
        # copy config first to avoid mutations through references
        self._conf = self._conf.copy()

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


    """
    Sensor Information Query APIs
    """

    def is_healthy(self):
        """
        Check if sensor is healthy under constraints passed in `options`.

        Raises:
            SensorInfoError: If an error occurs while gathering the sensor information.
        """
        raise NotImplementedError()


    def configured(self):
        with self._lock:
            return self._configured()


    """
    Private Functions
    """

    def _sanity_check_open(self):

        if not self._configured():
            raise RuntimeError(
                "Sensor must be configured before opening."
                )
        

    def _configured(self):
        return not self._conf.is_empty()
    

    def _fail(self):
        self._state = SensorState.ERRORED