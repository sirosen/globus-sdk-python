class GlobusError(Exception):
    """
    Root of the Globus Exception hierarchy.
    Stub class.
    """


class GlobusAPIError(GlobusError):
    def __init__(self, r, *args, **kw):
        self._underlying_response = r
        self.http_status = r.status_code
        if "application/json" in r.headers["Content-Type"]:
            try:
                self._load_from_json(r.json())
            except KeyError:
                self._load_from_text(r.text)
        else:
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
        self.code = data["code"]
        self.message = data["message"]

    def _load_from_text(self, text):
        """
        Load error data from a raw text body that is not JSON. Must set at
        least code and message instance variables.
        """
        self.code = "Error"
        self.message = text


class TransferAPIError(GlobusAPIError):
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
