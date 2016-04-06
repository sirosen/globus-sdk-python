class GlobusResponse(object):
    """
    Generic response object, with a single ``data`` member.
    """
    def __init__(self, data):
        """
        GlobusResponse objects *always* wrap some kind of data to return to a
        caller. Most basic actions on a GlobusResponse are just ways of
        interacting with this data.
        """
        self._data = data

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.data)

    @property
    def data(self):
        """
        Response data as a Python data structure. Usually a dict or
        list.
        """
        return self._data


class GlobusHTTPResponse(GlobusResponse):
    """
    Response object that wraps an HTTP response from the underlying HTTP
    library. If the response is JSON, the parsed data will be available in
    ``data``, otherwise ``data`` will be ``None`` and ``text_body`` should
    be used instead.

    :ivar http_status: HTTP status code returned by the server (int)
    :ivar content_type: Content-Type header returned by the server (str)
    """
    def __init__(self, http_response):
        # the API response as some form of HTTP response object will be the
        # underlying data of an API response
        GlobusResponse.__init__(self, http_response)
        # NB: the word 'code' is confusing because we use it in the
        # error body, and status_code is not much better. http_code, or
        # http_status_code if we wanted to be really explicit, is
        # clearer, but less consistent with requests (for better and
        # worse).
        self.http_status = http_response.status_code
        self.content_type = http_response.headers["Content-Type"]

    @property
    def data(self):
        try:
            return self.json_body
        # JSON decoding may raise a ValueError due to an invalid JSON
        # document. In the case of trying to fetch the "data" on an HTTP
        # response, this means we didn't get a JSON response. Rather than
        # letting the error bubble up, return None, as in "no data"
        # if the caller *really* wants the raw body of the response, they can
        # always use text_body
        except ValueError:
            return None

    @property
    def json_body(self):
        """
        Alias for ``data`` (contains the parsed JSON data), but will raise
        an exception if the response is not JSON instead of being ``None``.
        """
        return self._data.json()

    @property
    def text_body(self):
        """
        The raw response data, as a string.
        """
        return self._data.text
