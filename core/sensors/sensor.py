from ..stream_profile import StreamProfile


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
    def __init__(self):
        # Initialize an empty set for stream profiles
        self.profiles : set[StreamProfile] = set()

    def set_profiles(self, stream_profiles : set[StreamProfile]):
        self.profiles = stream_profiles.copy()

    def open(self):
        """
        Open the sensor physically.

        Raises:
            RuntimeError: If sensor couldn't be opened successfully.
        """
        raise NotImplementedError()

    def close(self):
        """
        Close the sensor physically.

        Raises:
            RuntimeError: If sensor couldn't be closed successfully.
        """

    def start(self):
        """
        Start the sensor (start streaming) physically.

        Raises:
            RuntimeError: If sensor couldn't be started successfully.
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop the sensor (end streaming) physically.

        Raises:
            RuntimeError: If sensor couldn't be stopped successfully.
        """
        raise NotImplementedError()

    def is_opened(self):
        """
        Check if sensor is physically in `Opened` state.

        Raises:
            RuntimeError: If an error occured during retrieving the sensor state.
        """
        raise NotImplementedError()

    def is_closed(self):
        """
        Check if sensor is physically in `Closed` state.

        Raises:
            RuntimeError: If an error occured during retrieving the sensor state.
        """
        return not self.is_opened()

    