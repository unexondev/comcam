class SensorError(Exception):
    """
    Base exception class for sensor-related errors.
    """

class SensorOpenError(SensorError):
    """
    Raised when sensor couldn't be opened.
    """

class SensorCloseError(SensorError):
    """
    Raised when sensor couldn't get closed.
    """

class SensorStartError(SensorError):
    """
    Raised when sensor couldn't be started.
    """

class SensorStopError(SensorError):
    """
    Raised when sensor couldn't be stopped.
    """

class SensorStateError(SensorError):
    """
    Raised when state information couldn't be gathered from sensor.
    """