class GlobusResponse(object):
    def __init__(self, data):
        """
        GlobusResponse objects *always* wrap some kind of data to return to a
        caller. Most basic actions on a GlobusResponse are just ways of
        interacting with this data.
        """
        self.data = data

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.data)


class GlobusHTTPResponse(GlobusResponse):
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
    def json_body(self):
        return self.data.json()

    @property
    def text_body(self):
        return self.data.text
