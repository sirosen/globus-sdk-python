from __future__ import annotations

import typing as t

import requests

from globus_sdk import exc


class TransferAPIError(exc.GlobusAPIError):
    """
    Error class for the Transfer API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides ``request_id``.

    :ivar request_id: Unique identifier for the request, which should be
                      provided when contacting support@globus.org.
    """

    def __init__(self, r: requests.Response) -> None:
        self.request_id: str | None = None
        super().__init__(r)

    def _get_args(self) -> list[t.Any]:
        args = super()._get_args()
        args.append(self.request_id)
        return args

    def _parse_response(self) -> bool:
        if not super()._parse_response():
            return False
        self.request_id = t.cast("dict[str, t.Any]", self.raw_json).get("request_id")
        return True
