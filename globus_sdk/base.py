import urllib
import json

import requests

from globus_sdk import config


class BaseClient(object):
    """
    Simple client with error handling for Globus REST APIs. It's a thin
    wrapper around a requests.Session object, with a simplified interface
    supplying only what we need for Globus APIs. The intention is to avoid
    directly exposing requests objects in the public API.
    """

    def __init__(self, service, environment="default", base_path=None):
        self.environment = environment
        self.base_url = config.get_service_url(environment, service)
        if base_path is not None:
            self.base_url = slash_join(self.base_url, base_path)
        print "base_url", self.base_url
        self._s = requests.Session()
        self._headers = dict(Accepts="application/json")
        # TODO: get this from config file, default True
        self._verify = True

    def set_auth_token(self, token):
        self._headers["Authorization"] = "Bearer %s" % token

    def qjoin_path(self, *parts):
        return "/" + "/".join(urllib.quote(part) for part in parts)

    def get(self, path, params=None, headers=None):
        return self._request("GET", path, params=params, headers=headers)

    def post(self, path, data=None, params=None, headers=None):
        return self._request("POST", path, data=data, params=params,
                             headers=headers)

    def delete(self, path, params=None, headers=None):
        return self._request("DELETE", path, params=params, headers=headers)

    def put(self, path, data=None):
        return self._request("PUT", path, data=data)

    def _request(self, method, path, data=None, params=None, headers=None):
        """
        :param data: data to send in the request body. If not a string,
                     it will be serialized with JSON.
        """
        # TODO: add a content_type param, and encode using
        # urlencode or json depending on type? While most of our APIs
        # use JSON, some of the auth APIs are based on existing specs
        # and use urlenocde instead.
        if data is not None and not isinstance(data, basestring):
            data = json.dumps(data)
        rheaders = dict(self._headers)
        if headers is not None:
            rheaders.update(headers)
        url = slash_join(self.base_url, path)
        print url
        r = self._s.request(method=method,
                            url=url,
                            headers=rheaders,
                            params=params,
                            data=data,
                            verify=self._verify)
        if 200 <= r.status_code < 400:
            return GlobusResponse(r)
        # TODO: an alternative to raising an error for 400+, we could
        # take an 'expected_status_code' param with a list of codes, and raise
        # an error if the code is not in the list. This is more flexible, and
        # what Transfer uses internally in it's globus auth lib, but it's
        # harder to use correctly.
        raise GlobusError(r)


class GlobusResponse(object):
    def __init__(self, r):
        self._r = r
        # NB: the word 'code' is confusing because we use it in the
        # error body, and status_code is not much better. http_code, or
        # http_status_code if we wanted to be really explicit, is
        # clearer, but less consistent with requests (for better and
        # worse).
        self.http_status = r.status_code
        self.content_type = r.headers["Content-Type"]

    @property
    def json(self):
        return self._r.json()

    @property
    def text(self):
        return self._r.text


class GlobusError(Exception):
    def __init__(self, r):
        if r.headers["Content-Type"] == "application/json":
            data = r.json()
            self.http_status = r.status_code
            self.code = data.get("code")
            self.message = data.get("message")
            # NB: Transfer API specific field
            self.request_id = data.get("request_id")
        else:
            self.http_status = r.status_code
            self.code = "BadRequest"
            self.message = "Requested URL is not an API resource"
            self.request_id = ""
        Exception.__init__(self, self.http_status, self.code,
                           self.message, self.request_id)


def slash_join(a, b):
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b
