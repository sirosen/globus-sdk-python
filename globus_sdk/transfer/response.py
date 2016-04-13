import json

from globus_sdk.response import GlobusHTTPResponse


class TransferResponse(GlobusHTTPResponse):
    """
    Base class for :class:`TransferClient <globus_sdk.TransferClient>`
    responses.
    """
    def __str__(self):
        # Make printing responses more convenient. Relies on the
        # fact that Transfer API responses are always JSON.
        return json.dumps(self.data, indent=2)


class IterableTransferResponse(TransferResponse):
    """
    Response class for non-paged list oriented resources. Allows top level
    fields to be accessed normally via standard item access, and also
    provides a convenient way to iterate over the sub-item list in the
    ``DATA`` key:

    >>> print("Path:", r["path"])
    >>> # Equivalent to: for item in r["DATA"]
    >>> for item in r:
    >>>     print(item["name"], item["type"])
    """
    def __iter__(self):
        return iter(self["DATA"])
