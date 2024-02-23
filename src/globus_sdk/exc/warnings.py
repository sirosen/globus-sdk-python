from __future__ import annotations

import warnings


class RemovedInV4Warning(DeprecationWarning):
    """
    This warning indicates that a feature or usage was detected which will be
    unsupported in globus-sdk version 4.

    Users are encouraged to resolve these warnings when possible, so that they will be
    able to upgrade to version 4 without issue.
    """


def warn_deprecated(message: str, stacklevel: int = 2) -> None:
    warnings.warn(message, RemovedInV4Warning, stacklevel=stacklevel)
