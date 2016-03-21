import json
import warnings
import base64

import requests

from six.moves.urllib.parse import quote

from globus_sdk import config, exc
from globus_sdk.response import GlobusHTTPResponse


class BaseClient(object):
    """
    Simple client with error handling for Globus REST APIs. It's a thin
    wrapper around a requests.Session object, with a simplified interface
    supplying only what we need for Globus APIs. The intention is to avoid
    directly exposing requests objects in the public API.
    """

    # Can be overridden by subclasses, but must be a subclass of GlobusError
    error_class = exc.GlobusAPIError
    response_class = GlobusHTTPResponse

    AUTH_TOKEN = "token"
    AUTH_BASIC = "basic"

    def __init__(self, service, environment=config.get_default_environ(),
                 base_path=None, auth_token=None):
        self.environment = environment
        self.base_url = config.get_service_url(environment, service)
        if base_path is not None:
            self.base_url = slash_join(self.base_url, base_path)
        self._session = requests.Session()
        self._headers = dict(Accept="application/json")
        self._auth = None


        if not auth_token:
            # potentially add an Authorization header, if a token is specified
            auth_token = config.get_auth_token(environment)
            warnings.warn(
                ('Providing raw Auth Tokens is not recommended, and is slated '
                 'for deprecation. If you use this feature, be ready to '
                 'transition to using a new authentication mechanism after we '
                 'announce its availability.'),
                PendingDeprecationWarning)
        if auth_token:
            self.set_auth_token(auth_token)

        self._verify = config.get_ssl_verify(environment)

    def set_auth_token(self, token):
        self.auth_type = self.AUTH_TOKEN
        self._headers["Authorization"] = "Bearer %s" % token

    def set_auth_basic(self, username, password):
        self.auth_type = self.AUTH_BASIC
        encoded = base64.b64encode("%s:%s" % (username, password))
        self._headers["Authorization"] = "Basic %s" % encoded

    def qjoin_path(self, *parts):
        return "/" + "/".join(quote(part) for part in parts)

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
            return self.response_class(r)
        raise self.error_class(r)


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


def merge_params(base_params, **more_params):
    """
    Merge additional keyword arguments into a base dictionary of keyword
    arguments. Only inserts additional kwargs which are not None.
    This way, we can accept a bunch of named kwargs, a collector of additional
    kwargs, and then put them together sensibly as arguments to another
    function (typically BaseClient.get() or a variant thereof).

    For example:

    >>> def ep_search(self, filter_scope=None, filter_fulltext=None, **params):
    >>>     # Yes, this is a side-effecting function, it doesn't return a new
    >>>     # dict because it's way simpler to update in place
    >>>     merge_params(
    >>>         params, filter_scope=filter_scope,
    >>>         filter_fulltext=filter_fulltext)
    >>>     return self.get('endpoint_search', params=params)

    this is a whole lot cleaner than the alternative form:

    >>> def ep_search(self, filter_scope=None, filter_fulltext=None, **params):
    >>>     if filter_scope is not None:
    >>>         params['filter_scope'] = filter_scope
    >>>     if filter_fulltext is not None:
    >>>         params['filter_scope'] = filter_scope
    >>>     return self.get('endpoint_search', params=params)

    the second form exposes a couple of dangers that are obviated in the first
    regarding correctness, like the possibility of doing

    >>>     if filter_scope:
    >>>         params['filter_scope'] = filter_scope

    which is wrong (!) because filter_scope='' is a theoretically valid,
    real argument we want to pass.
    The first form will also prove shorter and easier to write for the most
    part.
    """
    for param in more_params:
        if more_params[param] is not None:
            base_params[param] = more_params[param]
