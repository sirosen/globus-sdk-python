from __future__ import annotations

import typing as t

import requests

from globus_sdk import exc


class SearchAPIError(exc.GlobusAPIError):
    """
    Error class for the Search API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides ``error_data``.

    :ivar error_data: Additional object returned in the error response. May be
                      a dict, list, or None.
    """

    # the Search API always and only returns 'message' for string messages
    MESSAGE_FIELDS = ["message"]

    def __init__(self, r: requests.Response) -> None:
        self.error_data: dict[str, t.Any] | None = None
        super().__init__(r)

    def _parse_response(self) -> bool:
        if not super()._parse_response():
            return False
        self.error_data = self._dict_data.get("error_data")
        return True
