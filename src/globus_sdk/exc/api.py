from __future__ import annotations

import enum
import logging
import typing as t

import requests

from .base import GlobusError
from .err_info import ErrorInfoContainer
from .warnings import warn_deprecated

log = logging.getLogger(__name__)

_CACHE_SENTINEL = object()


class _ErrorFormat(enum.Enum):
    undefined = enum.auto()
    jsonapi = enum.auto()
    type_zero = enum.auto()


class GlobusAPIError(GlobusError):
    """
    Wraps errors returned by a REST API.

    :ivar int http_status: HTTP status code
    :ivar str code: Error code from the API or "Error" for unclassified errors
    :ivar str request_id: The 'request_id' included in the error data, if any.
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
        self.code: str | None = "Error"
        self.request_id: str | None = None
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

    def _get_mimetype(self, content_type: str) -> str:
        return content_type.split(";")[0].strip()

    def _jsonapi_mimetype(self) -> bool:
        if self.content_type is None:
            return False
        return self._get_mimetype(self.content_type) == "application/vnd.api+json"

    def _json_mimetype(self) -> bool:
        if self.content_type is None:
            return False
        mimetype = self._get_mimetype(self.content_type)
        if mimetype == "application/json":
            return True
        if mimetype.startswith("application/") and mimetype.endswith("+json"):
            return True
        return False

    @property
    def raw_json(self) -> dict[str, t.Any] | None:
        """
        Get the verbatim error message received from a Globus API, interpreted
        as JSON data

        If the body cannot be loaded as JSON, this is None
        """
        if self._cached_raw_json == _CACHE_SENTINEL:
            self._cached_raw_json = None
            if self._json_mimetype():
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
        args = [
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
        if self.request_id:
            args.append(self.request_id)
        return args

    def _parse_response(self) -> bool:
        """
        This is an intermediate step between 'raw_json' (loading bare JSON data)
        and the "real" parsing methods.

        In order to better support subclassing with short-circuiting behaviors if
        parsing goes awry, all of the parsing methods return True if parsing should
        continue or False if it was aborted.

        _parse_response() pulls the JSON body and does the following:

        - on non-dict JSON data, log and abort early. Don't error since this
          is already part of exception construction, just stop parsing.

        - Attempt to detect the error format in use, then dispatch to the relevant
          subparser: JSON:API, Type Zero, or Undefined

        - if subparsing succeeded, call the `_final_parse_callback` hook to allow
          subclasses to trivially add more computed attributes. This could also be
          done by altering `__init__` but it's nicer to have a dedicated hook because
          it is guaranteed to only be called if the rest of parsing succeeded
        """
        if self.raw_json is None:
            log.debug("Error body was not parsed as JSON")
            return False
        if not isinstance(self.raw_json, dict):
            log.warning(  # type: ignore[unreachable]
                "Error body could not be parsed as JSON because it was not a dict"
            )
            return False

        error_format = self._detect_error_format()
        subparse_result: bool
        if error_format == _ErrorFormat.jsonapi:
            subparse_result = self._parse_jsonapi_error_format()
        elif error_format == _ErrorFormat.type_zero:
            subparse_result = self._parse_type_zero_error_format()
        else:
            subparse_result = self._parse_undefined_error_format()

        if not subparse_result:
            return False
        return self._final_parse_callback()

    def _detect_error_format(self) -> _ErrorFormat:
        # if the JSON:API mimetype was used, inspect the data to make sure it is
        # well-formed
        if self._jsonapi_mimetype():
            errors = self._dict_data.get("errors")
            if not isinstance(errors, list):
                return _ErrorFormat.undefined
            elif len(errors) < 1:
                return _ErrorFormat.undefined
            elif not all(isinstance(error_doc, dict) for error_doc in errors):
                return _ErrorFormat.undefined

            # only use 'jsonapi' if everything checked out
            return _ErrorFormat.jsonapi

        # now evaluate attributes for Type Zero errors under the same paradigm
        # check each attribute and only return 'type_zero' if nothing failed

        if not isinstance(self._dict_data.get("code"), str):
            return _ErrorFormat.undefined
        elif not isinstance(self._dict_data.get("message"), str):
            return _ErrorFormat.undefined
        # request_id is not required, but must be a string if present
        elif "request_id" in self._dict_data and not isinstance(
            self._dict_data["request_id"], str
        ):
            return _ErrorFormat.undefined

        return _ErrorFormat.type_zero

    def _parse_jsonapi_error_format(self) -> bool:
        # parsing a JSON:API error is only called after the field type for 'errors'
        # has been checked
        # however, the nested/underlying fields will not have been checked yet
        self.errors = self._dict_data["errors"]
        self.code = self._extract_code_from_error_array(self.errors)
        self.messages = self._extract_messages_from_error_array(
            self.errors, ("detail", "title")
        )
        return True

    def _parse_type_zero_error_format(self) -> bool:
        # parsing a Type Zero error is only called after Type Zero has been detected
        # therefore, we already have assurances about the values in 'code' and 'message'
        # note that 'request_id' could be absent but *must* be a string if present
        self.code = self._dict_data["code"]
        self.messages = [self._dict_data["message"]]
        self.request_id = self._dict_data.get("request_id")
        return True

    def _parse_undefined_error_format(self) -> bool:
        # Undefined parsing: best effort support for unknown data shapes
        # this is also a great place for custom parsing to hook in for different APIs
        # if we know that there's an unusual format in use

        # attempt to pull out errors if possible
        if isinstance(self._dict_data.get("errors"), list):
            subdocuments = [
                subdoc
                for subdoc in self._dict_data["errors"]
                if isinstance(subdoc, dict)
            ]
            if subdocuments:
                self.errors = subdocuments

        # use 'code' if present and correct type
        if isinstance(self._dict_data.get("code"), str):
            self.code = t.cast(str, self._dict_data["code"])
        # otherwise, check if all 'errors' which contain a 'code' have the same one
        # if so, that will be safe to use instead
        elif self.errors:
            code = self._extract_code_from_error_array(self.errors)
            if code is not None:
                self.code = code

        # either there is an array of subdocument errors or there is not,
        # in which case we load only from the root doc
        self.messages = self._extract_messages_from_error_array(
            self.errors or [self._dict_data]
        )

        return True

    def _extract_messages_from_error_array(
        self,
        errors: list[dict[str, t.Any]],
        message_fields: t.Sequence[str] | None = None,
    ) -> list[str]:
        """
        Extract 'messages' from an array of errors (JSON:API or otherwise)

        This is done by checking each error document for the desired message fields and
        popping out the first such message for each document.
        """
        if message_fields is None:
            message_fields = self.MESSAGE_FIELDS

        ret: list[str] = []
        for doc in errors:
            for f in message_fields:
                if isinstance(doc.get(f), str):
                    log.debug("Loaded message from '%s' field", f)
                    ret.append(doc[f])
                    # NOTE! this break ensures we take only one field per error
                    # document (or subdocument) as the 'message'
                    # so that a doc like
                    #   {"message": "foo", "detail": "bar"}
                    # has a single message, "foo"
                    break

        return ret

    def _extract_code_from_error_array(
        self, errors: list[dict[str, t.Any]]
    ) -> str | None:
        """
        Extract a 'code' field from an array of errors (JSON:API or otherwise)

        This is done by checking if each error document has the same 'code'
        """
        codes: set[str] = set()
        for error in errors:
            if isinstance(error.get("code"), str):
                codes.add(error["code"])
        if len(codes) == 1:
            return codes.pop()
        return None

    def _final_parse_callback(self) -> bool:
        """
        A final internal callback for extra customizations after
        fully successful parsing.

        By default, does nothing.
        """
        return True
