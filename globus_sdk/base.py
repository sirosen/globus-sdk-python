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
        self._session = requests.Session()
        self._headers = dict(Accepts="application/json")
        # TODO: get this from config file, default True
        self._verify = True
        if "ec2" in self.base_url:
            self._verify = False

    def set_auth_token(self, token):
        self._headers["Authorization"] = "Bearer %s" % token

    def qjoin_path(self, *parts):
        return "/" + "/".join(urllib.quote(part) for part in parts)

    def get(self, path, params=None, headers=None, auth=None):
        return self._request("GET", path, params=params, headers=headers,
                             auth=auth)

    def post(self, path, json_body=None, params=None, headers=None,
             text_body=None, auth=None):
        return self._request("POST", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body, auth=auth)

    def delete(self, path, params=None, headers=None, auth=None):
        return self._request("DELETE", path, params=params,
                             headers=headers, auth=auth)

    def put(self, path, json_body=None, params=None, headers=None,
            text_body=None, auth=None):
        return self._request("PUT", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body, auth=auth)

    def _request(self, method, path, params=None, headers=None,
                 json_body=None, text_body=None, auth=None):
        """
        :param json_body: Python data structure to send in the request body
                          serialized as JSON
        :param text_body: string to send in the request body
        """
        if json_body is not None:
            assert text_body is None
            text_body = json.dumps(json_body)
        rheaders = dict(self._headers)
        if headers is not None:
            rheaders.update(headers)
        url = slash_join(self.base_url, path)
        r = self._session.request(method=method,
                                  url=url,
                                  headers=rheaders,
                                  params=params,
                                  data=text_body,
                                  verify=self._verify,
                                  auth=auth)
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
        self._underlying_request = r
        # NB: the word 'code' is confusing because we use it in the
        # error body, and status_code is not much better. http_code, or
        # http_status_code if we wanted to be really explicit, is
        # clearer, but less consistent with requests (for better and
        # worse).
        self.http_status = r.status_code
        self.content_type = r.headers["Content-Type"]

    @property
    def json_body(self):
        return self._underlying_request.json()

    @property
    def text_body(self):
        return self._underlying_request.text


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
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
    """
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b
