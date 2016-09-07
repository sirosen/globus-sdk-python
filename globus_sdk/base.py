import json

import requests

from six.moves.urllib.parse import quote

from globus_sdk import config, exc
from globus_sdk.version import __version__
from globus_sdk.response import GlobusHTTPResponse


class BaseClient(object):
    r"""
    Simple client with error handling for Globus REST APIs. Implemented
    as a wrapper around a ``requests.Session`` object, with a simplified
    interface that does not directly expose anything from requests.

    :param authorizer: optional :class:`GlobusAuthorizer \
    <globus_sdk.authorizers.GlobusAuthorizer>` which will generate
    Authorization headers
    :param app_name: optional "nice name" for the application

    ``app_name`` has no bearing on the semantics of client actions. It is just
    passed as part of the User-Agent string, and may be useful when debugging
    issues with the Globus Team.

    All other arguments are for internal use and should be ignored.


    You should *never* try to directly instantiate a ``BaseClient``.
    """

    # Can be overridden by subclasses, but must be a subclass of GlobusError
    error_class = exc.GlobusAPIError
    default_response_class = GlobusHTTPResponse

    BASE_USER_AGENT = 'globus-sdk-py-{0}'.format(__version__)

    def __init__(self, service, environment=config.get_default_environ(),
                 base_path=None, authorizer=None, app_name=None):
        self.environment = environment
        self.authorizer = authorizer

        self.base_url = config.get_service_url(environment, service)
        if base_path is not None:
            self.base_url = slash_join(self.base_url, base_path)

        # setup the basics for wrapping a Requests Session
        # including basics for internal header dict
        self._session = requests.Session()
        self._headers = {
            'Accept': 'application/json',
            'User-Agent': self.BASE_USER_AGENT
        }

        # verify SSL? Usually true
        self._verify = config.get_ssl_verify(environment)

        # set application name if given
        self.app_name = None
        if app_name is not None:
            self.set_app_name(app_name)

    def set_app_name(self, app_name):
        """
        Set an application name to send to Globus services as part of the User
        Agent.

        Application developers are encouraged to set an app name as a courtesy
        to the Globus Team, and to potentially speed resolution of issues when
        interacting with Globus Support.
        """
        self.app_name = app_name
        self._headers['User-Agent'] = '{0}/{1}'.format(self.BASE_USER_AGENT,
                                                       app_name)

    def qjoin_path(self, *parts):
        return "/" + "/".join(quote(part) for part in parts)

    def get(self, path, params=None, headers=None,
            response_class=None, no_auth_header=False, retry_401=True):
        """
        Make a GET request to the specified path.

        :param path: path for the request, with or without leading slash
        :param params: dict to be encoded as a query string
        :param headers: dict of HTTP headers to add to the request
        :param response_class: class for response object, overrides the
                               client's ``default_response_class``
        :param no_auth_header: Suppress the Authorization header
        :param retry_401: Retry on 401 responses with fresh Authorization if
                          ``self.authorizer`` supports it

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("GET", path, params=params, headers=headers,
                             response_class=response_class,
                             no_auth_header=no_auth_header,
                             retry_401=retry_401)

    def post(self, path, json_body=None, params=None, headers=None,
             text_body=None, response_class=None, no_auth_header=False,
             retry_401=True):
        """
        Make a POST request to the specified path.

        :param path: path for the request, with or without leading slash
        :param params: dict to be encoded as a query string
        :param headers: dict of HTTP headers to add to the request
        :param json_body: dict that will be encoded as a JSON request body
        :param text_body: raw string that will be the request body
        :param response_class: class for response object, overrides the
                               client's ``default_response_class``
        :param no_auth_header: Suppress the Authorization header
        :param retry_401: Retry on 401 responses with fresh Authorization if
                          ``self.authorizer`` supports it

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("POST", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body,
                             response_class=response_class,
                             no_auth_header=no_auth_header,
                             retry_401=retry_401)

    def delete(self, path, params=None, headers=None,
               response_class=None, no_auth_header=False, retry_401=True):
        """
        Make a DELETE request to the specified path.

        :param path: path for the request, with or without leading slash
        :param params: dict to be encoded as a query string
        :param headers: dict of HTTP headers to add to the request
        :param response_class: class for response object, overrides the
                               client's ``default_response_class``
        :param no_auth_header: Suppress the Authorization header
        :param retry_401: Retry on 401 responses with fresh Authorization if
                          ``self.authorizer`` supports it

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("DELETE", path, params=params,
                             headers=headers,
                             response_class=response_class,
                             no_auth_header=no_auth_header,
                             retry_401=retry_401)

    def put(self, path, json_body=None, params=None, headers=None,
            text_body=None, response_class=None, no_auth_header=False,
            retry_401=True):
        """
        Make a PUT request to the specified path.

        :param path: path for the request, with or without leading slash
        :param params: dict to be encoded as a query string
        :param headers: dict of HTTP headers to add to the request
        :param json_body: dict that will be encoded as a JSON request body
        :param text_body: raw string that will be the request body
        :param response_class: class for response object, overrides the
                               client's ``default_response_class``
        :param no_auth_header: Suppress the Authorization header
        :param retry_401: Retry on 401 responses with fresh Authorization if
                          ``self.authorizer`` supports it

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        return self._request("PUT", path, json_body=json_body, params=params,
                             headers=headers, text_body=text_body,
                             response_class=response_class,
                             no_auth_header=no_auth_header,
                             retry_401=retry_401)

    def _request(self, method, path, params=None, headers=None,
                 json_body=None, text_body=None,
                 response_class=None, no_auth_header=False, retry_401=True):
        """
        :param method: HTTP request method, as an all caps string
        :param path: path for the request, with or without leading slash
        :param headers: dict containing additional headers for the request
        :param params: dict to be encoded as a query string
        :param json_body: dict that will be encoded as a JSON request body
        :param text_body: raw string that will be the request body
        :param response_class: class for response object, overrides the
                               client's ``default_response_class``
        :param no_auth_header: Suppress the Authorization header
        :param retry_401: Retry on 401 responses with fresh Authorization if
                          ``self.authorizer`` supports it

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        if json_body is not None:
            assert text_body is None
            text_body = json.dumps(json_body)

        # copy
        rheaders = dict(self._headers)
        # expand
        if headers is not None:
            rheaders.update(headers)

        # add Authorization header, or (if it's a NullAuthorizer) possibly
        # explicitly remove the Authorization header
        if self.authorizer is not None and not no_auth_header:
            self.authorizer.set_authorization_header(rheaders)

        url = slash_join(self.base_url, path)

        # because a 401 can trigger retry, we need to wrap the retry-able thing
        # in a method
        def send_request():
            try:
                return self._session.request(
                    method=method, url=url, headers=rheaders, params=params,
                    data=text_body, verify=self._verify)
            except requests.Timeout as e:
                raise exc.TimeoutError(*e.args)
            except requests.ConnectionError as e:
                raise exc.ConnectionError(*e.args)
            except requests.RequestException as e:
                raise exc.NetworkError(*e.args)

        # initial request
        r = send_request()

        # potential 401 retry handling
        if r.status_code == 401 and retry_401 and (
                self.authorizer is not None and not no_auth_header):
            # note that although handle_missing_authorization returns a T/F
            # value, it may actually mutate the state of the authorizer and
            # therefore change the value set by the `set_authorization_header`
            # method
            if self.authorizer.handle_missing_authorization():
                self.authorizer.set_authorization_header(rheaders)
                r = send_request()

        if 200 <= r.status_code < 400:
            if response_class is None:
                return self.default_response_class(r)
            else:
                return response_class(r)

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


def assert_exclusive_params(method_or_constructor_name, detailed_message,
                            **params):
    """
    Given a method or constructor, and two parameters with their names (given
    as keyword arguments for convenience), ensures that at least one of the two
    is None.
    This is a helper for writing (usually) constructors which have strict
    requirements on what parameters are allowed.

    Additionally, you are required to provide a message with some more detail
    on what's going on or why these are exclusive, which will be formatted into
    the exception message.
    """
    if not len(params) == 2:
        raise ValueError(
            'assert_exclusive_params() requires EXACTLY 2 keyword arguments')

    # get items in order, then pull them apart so we can actually work with
    # them
    items = params.items()
    k1, v1 = items[0]
    k2, v2 = items[1]

    if v1 is not None and v2 is not None:
        raise ValueError(
            '{0} cannot take both {1} and {2} as arguments: {3}'.format(
                method_or_constructor_name, k1, k2, detailed_message))
