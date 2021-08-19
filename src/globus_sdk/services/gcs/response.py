from globus_sdk.response import IterableResponse


class IterableGCSResponse(IterableResponse):
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

    default_iter_key = "data"
