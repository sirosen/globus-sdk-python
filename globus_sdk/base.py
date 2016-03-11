import urllib
import json
import warnings

import requests

from globus_sdk import config


class GlobusError(Exception):
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
        Exception.__init__(self, *args)

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


class BaseClient(object):
    """
    Simple client with error handling for Globus REST APIs. It's a thin
    wrapper around a requests.Session object, with a simplified interface
    supplying only what we need for Globus APIs. The intention is to avoid
    directly exposing requests objects in the public API.
    """

    # Can be overridden by subclasses, but must be a subclass of GlobusError
    error_class = GlobusError

    def __init__(self, service, environment="default", base_path=None):
        self.environment = environment
        self.base_url = config.get_service_url(environment, service)
        if base_path is not None:
            self.base_url = slash_join(self.base_url, base_path)
        self._session = requests.Session()
        self._headers = dict(Accepts="application/json")

        # potentially add an Authorization header, if a token is specified
        auth_token = config.get_auth_token(environment)
        if auth_token:
            warnings.warn(
                ('Providing raw Auth Tokens is not recommended, and is slated '
                 'for deprecation. If you use this feature, be ready to '
                 'transition to using a new authentication mechanism after we '
                 'announce its availability.'),
                PendingDeprecationWarning)
            self.set_auth_token(auth_token)

        self._verify = config.get_ssl_verify(environment)

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
        raise self.error_class(r)


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
