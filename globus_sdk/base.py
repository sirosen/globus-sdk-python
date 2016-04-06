import json
import base64

import requests

from six.moves.urllib.parse import quote

from globus_sdk import config, exc
from globus_sdk.response import GlobusHTTPResponse


class BaseClient(object):
    """
    Simple client with error handling for Globus REST APIs. Implemented
    as a wrapper around a ``requests.Session`` object, with a simplified
    interface that does not directly expose anything from requests.
    """

    # Can be overridden by subclasses, but must be a subclass of GlobusError
    error_class = exc.GlobusAPIError
    response_class = GlobusHTTPResponse

    AUTHTYPE_TOKEN = "token"
    AUTHTYPE_BASIC = "basic"

    def __init__(self, service, environment=config.get_default_environ(),
                 base_path=None, token=None):
        self.environment = environment
        self.base_url = config.get_service_url(environment, service)
        if base_path is not None:
            self.base_url = slash_join(self.base_url, base_path)
        self._session = requests.Session()
        self._headers = dict(Accept="application/json")
        self._auth = None

        if not token:
            token = self.config_load_token()
        self.set_token(token)

        self._verify = config.get_ssl_verify(environment)

    def set_token(self, token):
        """Set bearer token authentication for this client."""
        self.auth_type = self.AUTHTYPE_TOKEN
        self._headers["Authorization"] = "Bearer %s" % token

    def set_auth_basic(self, username, password):
        """Set basic authentication for this client."""
        self.auth_type = self.AUTHTYPE_BASIC
        encoded = base64.b64encode("%s:%s" % (username, password))
        self._headers["Authorization"] = "Basic %s" % encoded

    def config_load_token(self):
        raise NotImplementedError(
            ('The BaseClient does not have a service token type associated '
             'with it. config_load_token() must be defined by a subclass '
             'because tokens are associated with services.'))

    def qjoin_path(self, *parts):
        return "/" + "/".join(quote(part) for part in parts)

    def get(self, path, params=None, headers=None, auth=None):
        """
        Make a GET request to the specified path.

        :param params: dict to be encoded as a query string

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("GET", path, params=params, headers=headers,
                             auth=auth)

    def post(self, path, json_body=None, params=None, headers=None,
             text_body=None, auth=None):
        """
        Make a POST request to the specified path, with optional body in
        either ``json_body`` (python data that will be encoded as JSON) or
        ``text_body``.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("POST", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body, auth=auth)

    def delete(self, path, params=None, headers=None, auth=None):
        """
        Make a DELETE request to the specified path.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("DELETE", path, params=params,
                             headers=headers, auth=auth)

    def put(self, path, json_body=None, params=None, headers=None,
            text_body=None, auth=None):
        """
        Make a PUT request to the specified path.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("PUT", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body, auth=auth)

    def _request(self, method, path, params=None, headers=None,
                 json_body=None, text_body=None, auth=None):
        """
        :param method: HTTP request method, as an all caps string
        :param headers: dict containing additional headers for the request
        :param params: dict to be encoded as a query string
        :param auth: tuple of (user, password) for basic auth [DEPRECATED]
        :param json_body: Python data structure to send in the request body
                          serialized as JSON
        :param text_body: string to send in the request body

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
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
