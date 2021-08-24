from typing import Any

from globus_sdk.response import GlobusHTTPResponse, IterableResponse


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


class SingletonGCSResponse(GlobusHTTPResponse):
    """
    A "singleton" response looks for a "data" array in the response data, which is
    expected to have exactly one (dict) element. This is presented as the ``data``
    property of the response.

    The full response data is available as ``original_data``.

    If the expected data shape is not satisfied, the ``data`` will be the full response
    data (identical to ``original_data``).
    """

    @property
    def original_data(self) -> Any:
        """
        The full, parsed JSON response data.
        ``None`` if the data cannot be parsed as JSON.
        """
        return self._parsed_json

    def data_has_expected_shape(self) -> bool:
        """
        True or False depending on whether or not the response data was shaped like a
        SingletonGCSResponse. The response object may still be used when this is false,
        but the results could be unexpected.
        """
        return (
            isinstance(self._parsed_json, dict)
            and isinstance(self._parsed_json.get("data"), list)
            and len(self._parsed_json["data"]) == 1
        )

    @property
    def data(self) -> Any:
        if self.data_has_expected_shape():
            return self._parsed_json["data"][0]
        return self._parsed_json
