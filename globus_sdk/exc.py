import logging
import textwrap

logger = logging.getLogger(__name__)


class GlobusError(Exception):
    """
    Root of the Globus Exception hierarchy.
    Stub class.
    """


class GlobusAPIError(GlobusError):
    """
    Wraps errors returned by a REST API.

    :ivar http_status: HTTP status code (int)
    :ivar code: Error code from the API (str),
                or "Error" for unclassified errors
    :ivar message: Error message from the API. In general, this will be more
                   useful to developers, but there may be cases where it's
                   suitable for display to end users.
    """
    def __init__(self, r, *args, **kw):
        self._underlying_response = r
        self.http_status = r.status_code
        if "application/json" in r.headers["Content-Type"]:
            logger.debug(('Content-Type on error is application/json. '
                          'Doing error load from JSON'))
            try:
                self._load_from_json(r.json())
            except KeyError:
                logger.error(('Error body could not be JSON decoded! '
                              'This means the Content-Type is wrong, or the '
                              'body is malformed!'))
                self._load_from_text(r.text)
        else:
            logger.debug(('Content-Type on error is unknown. '
                          'Failing over to error load as text (default)'))
            # fallback to using the entire body as the message for all
            # other types
            self._load_from_text(r.text)
        args = self._get_args()
        GlobusError.__init__(self, *args)

    def _get_args(self):
        """
        Get arguments to pass to the Exception base class. These args are
        displayed in stack traces.
        """
        return (self.http_status, self.code, self.message)

    def _load_from_json(self, data):
        """
        Load error data from a JSON document. Must set at least
        code and message instance variables.
        """
        if "errors" in data:
            if len(data["errors"]) != 1:
                logger.warn(("Doing JSON load of error response with multiple "
                             "errors. Exception data will only include the "
                             "first error, but there are really {} errors")
                            .format(len(data["errors"])))
            # TODO: handle responses with more than one error
            data = data["errors"][0]
        self.code = data["code"]
        if "message" in data:
            logger.debug(("Doing JSON load of error response with 'message' "
                          "field. There may also be a useful 'detail' field "
                          "to inspect"))
            self.message = data["message"]
        else:
            self.message = data["detail"]

    def _load_from_text(self, text):
        """
        Load error data from a raw text body that is not JSON. Must set at
        least code and message instance variables.
        """
        self.code = "Error"
        self.message = text


class TransferAPIError(GlobusAPIError):
    """
    Error class for the Transfer API client. In addition to the
    inherited ``code`` and ``message`` instance variables, provides:

    :ivar request_id: Unique identifier for the request, which should be
                      provided when contacting support@globus.org.
    """
    def __init__(self, r):
        self.request_id = None
        GlobusAPIError.__init__(self, r)

    def _get_args(self):
        return (self.http_status, self.code, self.message, self.request_id)

    def _load_from_json(self, data):
        self.code = data["code"]
        self.message = data["message"]
        self.request_id = data["request_id"]


class PaginationOverrunError(GlobusError):
    """
    Paginated results exceeded a limit set by our API. Too many pages of
    results were being requested, and the API maximum would be exceeded.
    """


class InvalidDocumentBodyError(GlobusError):
    """
    Paginated results exceeded a limit set by our API. Too many pages of
    results were being requested, and the API maximum would be exceeded.
    """


# Thin wrappers around requests exceptions, so the SDK is API independent.
class NetworkError(GlobusError):
    """
    Error communicating with the REST API server.
    """


class GlobusTimeoutError(NetworkError):
    """The REST request timed out."""


class GlobusConnectionError(NetworkError):
    """A connection error occured while making a REST request."""


class GlobusOptionalDependencyError(GlobusError, NotImplementedError):
    """
    Error class for attempts to use features only enabled via optional
    dependencies without those dependencies installed.

    **Parameters**

        ``dep_names`` (*string list*)
          Package names for the required dependencies for this feature,
          possibly also encoding the version requirements for those packages.

        ``feature_name`` (*string*)
          Name of the method, property, class, or other construct which
          requires these dependencies

        ``message`` (*string*)
          An additional message to include
    """
    def __init__(self, dep_names, feature_name):
        self.message = textwrap.dedent("""\
        You are missing optional dependencies required in order to use {0}
        In order to use this feature of the Globus SDK, you must install:
          {1}

        For more information, visit our optional dependency documentation:
        http://globus.github.io/globus-sdk-python/optional_dependencies.html
        """.format(feature_name, "\n  ".join(dep_names)))
