from __future__ import annotations

import logging
import typing as t

import requests

from .base import GlobusError
from .err_info import ErrorInfoContainer
from .warnings import warn_deprecated

log = logging.getLogger(__name__)

_CACHE_SENTINEL = object()


class GlobusAPIError(GlobusError):
    """
    Wraps errors returned by a REST API.

    :ivar int http_status: HTTP status code
    :ivar str code: Error code from the API or "Error" for unclassified errors
    :ivar list[str] messages: A list of error messages, extracted from the response
        data. If the data cannot be parsed or does not contain any clear message fields,
        this list may be empty.
    :ivar list[dict] errors: A list of sub-error documents, as would be presented by
        JSON:API APIs and similar interfaces. If no such parse succeeds, the list will
        be empty.
    """

    MESSAGE_FIELDS = ["message", "detail", "title"]
    RECOGNIZED_AUTHZ_SCHEMES = ["bearer", "basic", "globus-goauthtoken"]

    def __init__(self, r: requests.Response, *args: t.Any, **kwargs: t.Any):
        self._cached_raw_json: t.Any = _CACHE_SENTINEL

        self.http_status = r.status_code
        # defaults, may be rewritten during parsing
        self.code = "Error"
        self.messages: list[str] = []
        self.errors: list[dict[str, t.Any]] = []

        self._info: ErrorInfoContainer | None = None
        self._underlying_response = r
        self._parse_response()
        super().__init__(*self._get_args())

    @property
    def message(self) -> str | None:
        """
        An error message from the API.

        If there are multiple messages available, this will contain all messages joined
        with semicolons. If there is no message available, this will be ``None``.
        """
        if self.messages:
            return "; ".join(self.messages)
        return None

    @message.setter
    def message(self, value: str) -> None:
        warn_deprecated(
            "Setting a message on GlobusAPIError objects is deprecated. "
            "This overwrites any parsed messages. Append to 'messages' instead."
        )
        self.messages = [value]

    @property
    def http_reason(self) -> str:
        """
        The HTTP reason string from the response.

        This is the part of the status line after the status code, and typically is a
        string description of the status. If the status line is
        ``HTTP/1.1 404 Not Found``, then this is the string ``"Not Found"``.
        """
        return self._underlying_response.reason

    @property
    def headers(self) -> t.Mapping[str, str]:
        """
        The HTTP response headers as a case-insensitive mapping.

        For example, ``headers["Content-Length"]`` and ``headers["content-length"]`` are
        treated as equivalent.
        """
        return self._underlying_response.headers

    @property
    def content_type(self) -> str | None:
        return self.headers.get("Content-Type")

    def _json_content_type(self) -> bool:
        r = self._underlying_response
        return "Content-Type" in r.headers and (
            "application/json" in r.headers["Content-Type"]
        )

    @property
    def raw_json(self) -> dict[str, t.Any] | None:
        """
        Get the verbatim error message received from a Globus API, interpreted
        as JSON data

        If the body cannot be loaded as JSON, this is None
        """
        if self._cached_raw_json == _CACHE_SENTINEL:
            self._cached_raw_json = None
            if self._json_content_type():
                try:
                    # technically, this could be a non-dict JSON type, like a list or
                    # string but in those cases the user can just cast -- the "normal"
                    # case is a dict
                    self._cached_raw_json = self._underlying_response.json()
                except ValueError:
                    log.error(
                        "Error body could not be JSON decoded! "
                        "This means the Content-Type is wrong, or the "
                        "body is malformed!"
                    )
        return t.cast("dict[str, t.Any]", self._cached_raw_json)

    @property
    def _dict_data(self) -> dict[str, t.Any]:
        """
        A "type asserting" wrapper over raw_json which errors if the type is not dict.
        """
        if not isinstance(self.raw_json, dict):
            raise ValueError("cannot use _dict_data when data is non-dict type")
        return self.raw_json

    @property
    def text(self) -> str:
        """
        Get the verbatim error message received from a Globus API as a *string*
        """
        return self._underlying_response.text

    @property
    def raw_text(self) -> str:
        """
        Deprecated alias of the ``text`` property.
        """
        warn_deprecated(
            "The 'raw_text' property of GlobusAPIError objects is deprecated. "
            "Use the 'text' property instead."
        )
        return self.text

    @property
    def binary_content(self) -> bytes:
        """
        The error message received from a Globus API in bytes.
        """
        return self._underlying_response.content

    @property
    def info(self) -> ErrorInfoContainer:
        """
        An ``ErrorInfoContainer`` with parsed error data. The ``info`` of an error is
        guaranteed to be present, but all of its contents may be falsey if the error
        could not be parsed.
        """
        if self._info is None:
            json_data = self.raw_json if isinstance(self.raw_json, dict) else None
            self._info = ErrorInfoContainer(json_data)
        return self._info

    def _get_request_authorization_scheme(self) -> str | None:
        try:
            authz_h = self._underlying_response.request.headers["Authorization"]
            authz_scheme = authz_h.split()[0]
            if authz_scheme.lower() in self.RECOGNIZED_AUTHZ_SCHEMES:
                return authz_scheme
        except (IndexError, KeyError):
            pass
        return None

    def _get_args(self) -> list[t.Any]:
        """
        Get arguments to pass to the Exception base class. These args are
        displayed in stack traces.
        """
        return [
            self._underlying_response.request.method,
            self._underlying_response.url,
            self._get_request_authorization_scheme(),
            self.http_status,
            self.code,
            # if the message is "", try using response reason
            # for details on these, and some examples, see
            #   https://datatracker.ietf.org/doc/html/rfc7231#section-6.1
            self.message or self._underlying_response.reason,
        ]

    def _parse_response(self) -> bool:
        """
        This is an intermediate step between 'raw_json' (loading bare JSON data)
        and the "real" parsing methods.
        In order to better support subclass usage, this returns True if parsing should
        continue or False if it was aborted.

        _parse_response() pulls the JSON body and does the following:
        - on non-dict JSON data, log and abort early. Don't error since this
          is already part of exception construction, just stop parsing.
        - parse any array of subdocument errors, tailored towards JSON:API
          (_parse_errors_array)
        - parse the code field from the document root
          (_parse_code)
        - if there are multiple sub-errors, extract messages from each of them
          (_parse_messages)

        Parsing the 'errors' array can be overridden to support custom error schemas,
        but by default it sniffs for JSON:API formatted data by looking for an 'errors'
        array and filtering it to dict members.
        """
        if self.raw_json is None:
            log.debug("Error body was not parsed as JSON")
            return False
        if not isinstance(self.raw_json, dict):
            log.warning(  # type: ignore[unreachable]
                "Error body could not be parsed as JSON because it was not a dict"
            )
            return False

        # at this point, the data has been confirmed to be a JSON object, so we can use
        # `_dict_data` to get a well-typed version of it
        self._parse_errors_array()
        self._parse_code()
        self._parse_messages()
        return True

    def _parse_errors_array(self) -> None:
        """
        Extract any array of subdocument errors into the `errors` array.

        This should be the first parsing component called.
        """
        if isinstance(self._dict_data.get("errors"), list):
            subdocuments = [
                subdoc
                for subdoc in self._dict_data["errors"]
                if isinstance(subdoc, dict)
            ]
            if subdocuments:
                self.errors = subdocuments

    def _parse_code(self) -> None:
        # use 'code' if present and correct type
        if isinstance(self._dict_data.get("code"), str):
            self.code = t.cast(str, self._dict_data["code"])
        # otherwise, check if all 'errors' which contain a 'code' have the same one
        # if so, that will be safe to use instead
        elif self.errors:
            codes: set[str] = set()
            for error in self.errors:
                if isinstance(error.get("code"), str):
                    codes.add(error["code"])
            if len(codes) == 1:
                self.code = codes.pop()

    def _parse_messages(self) -> None:
        # either there is an array of subdocument errors or there is not,
        # in which case we load only from the root doc
        for doc in self.errors or [self._dict_data]:
            for f in self.MESSAGE_FIELDS:
                if isinstance(doc.get(f), str):
                    log.debug("Loaded message from '%s' field", f)
                    self.messages.append(doc[f])
                    # NOTE! this break ensures we take only one field per error
                    # document (or subdocument) as the 'message'
                    # so that a doc like
                    #   {"message": "foo", "detail": "bar"}
                    # has a single message, "foo"
                    break
