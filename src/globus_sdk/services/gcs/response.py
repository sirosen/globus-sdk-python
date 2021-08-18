from typing import Any

from globus_sdk.response import GlobusHTTPResponse, IterOnIterKeyMixin


class IterableGCSResponse(GlobusHTTPResponse, IterOnIterKeyMixin):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    ``data`` key:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r["data"]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """

    def __init__(self, *args: Any, iter_key: str = "data", **kwargs: Any) -> None:
        self.iter_key = iter_key
        super().__init__(*args, **kwargs)
