from typing import Any

from ..profile import StreamProfile
from comcam.util.formatter import Formatter


class ProfileLifter:
    """
    An interface that defines how to lift backend-specific
    stream profiles to the `StreamProfile` objects.
    """

    @classmethod
    def lift(cls, backend_profile : object) -> StreamProfile:
        """
        Returns unformatted `StreamProfile` equivalent
        of backend-specific stream profile.

        Args:
            backend_profile: A `StreamProfile` instance to be lifted.

        Returns:
            The equivalent `StreamProfile` instance after lifting.

        Raises:
            NotImplementedError: If backend-specific profile is not implemented.
        """
        raise NotImplementedError()