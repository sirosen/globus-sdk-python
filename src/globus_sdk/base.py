import logging
import typing
import urllib.parse


from globus_sdk import config, exc, utils
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.transport import RequestsTransport
from globus_sdk.version import __version__

log = logging.getLogger(__name__)


class BaseClient:
    r"""
    Simple client with error handling for Globus REST APIs. Implemented
    as a wrapper around a ``requests.Session`` object, with a simplified
    interface that does not directly expose anything from requests.

    You should *never* try to directly instantiate a ``BaseClient``.

    :param authorizer: A ``GlobusAuthorizer`` which will generate Authorization headers
    :type authorizer: :class:`GlobusAuthorizer\
        <globus_sdk.authorizers.base.GlobusAuthorizer>`
    :param app_name: Optional "nice name" for the application. Has no bearing on the
        semantics of client actions. It is just passed as part of the User-Agent
        string, and may be useful when debugging issues with the Globus Team
    :type app_name: str
    :param http_timeout: Number of seconds to wait on HTTP connections. Default is 60.
        A value of ``-1`` indicates that no timeout should be used (requests can hang
        indefinitely).
    :type http_timeout: float

    All other parameters are for internal use and should be ignored.
    """
    # service name is used to lookup a service URL from config
    service_name: str = "_base"
    # path under the client base URL
    base_path: str = "/"

    # Can be overridden by subclasses, but must be a subclass of GlobusError
    error_class: typing.Type[exc.GlobusAPIError] = exc.GlobusAPIError
    default_response_class: typing.Type[GlobusHTTPResponse] = GlobusHTTPResponse

    BASE_USER_AGENT = f"globus-sdk-py-{__version__}"

    def __init__(
        self,
        environment=None,
        base_url=None,
        authorizer=None,
        app_name=None,
        http_timeout: typing.Optional[float] = None,
        *args,
        **kwargs,
    ):
        # explicitly check the `service_name` to ensure that it was set
        #
        # unfortunately, we can't rely on declaring BaseClient as an ABC because it
        # doesn't have any abstract methods
        #
        # if we declarse `service_name` without a value, we get AttributeError on access
        # instead of the (desired) TypeError when instantiating a BaseClient because
        # it's abstract
        if self.service_name == "_base":
            raise NotImplementedError(
                "Cannot instantiate clients which do not set a 'service_name'"
            )
        log.info(
            f'Creating client of type {type(self)} for service "{self.service_name}"'
        )

        # if an environment was passed, it will be used, but otherwise lookup
        # the env var -- and in the special case of `production` translate to
        # `default`, regardless of the source of that value
        # logs the environment when it isn't `default`
        self.environment = config.get_environment_name(environment)

        self.authorizer = authorizer

        self.base_url = utils.slash_join(
            config.get_service_url(self.environment, self.service_name)
            if base_url is None
            else base_url,
            self.base_path,
        )

        # HTTP connection timeout
        # this is passed verbatim to `requests`, and we therefore technically
        # support a tuple for connect/read timeouts, but we don't need to
        # advertise that... Just declare it as an float value
        if http_timeout is None:
            http_timeout = config.get_http_timeout(self.environment)
        # handle -1 by passing None to requests
        if http_timeout == -1:
            http_timeout = None

        self._transport = RequestsTransport(
            self.BASE_USER_AGENT,
            # verify SSL? Usually true
            config.get_ssl_verify(),
            http_timeout=config.get_http_timeout(http_timeout),
        )

        # set application name if given
        self._app_name = None
        if app_name is not None:
            self.app_name = app_name

    def __getstate__(self):
        """
        Render to a serializable dict for pickle.dump(s)
        """
        log.info("__getstate__() called; client being pickled")
        d = dict(self.__dict__)  # copy
        return d

    def __setstate__(self, d):
        """
        Load from a serialized format, as in pickle.load(s)
        """
        self.__dict__.update(d)
        log.info("__setstate__() finished; client unpickled")

    @property
    def app_name(self):
        return self._app_name

    @app_name.setter
    def app_name(self, value):
        """
        Set an application name to send to Globus services as part of the User
        Agent.

        Application developers are encouraged to set an app name as a courtesy
        to the Globus Team, and to potentially speed resolution of issues when
        interacting with Globus Support.
        """
        self._app_name = value
        self._transport.user_agent = f"{self.BASE_USER_AGENT}/{value}"

    def qjoin_path(self, *parts: str) -> str:
        return "/" + "/".join(urllib.parse.quote(part) for part in parts)

    def get(
        self, path, *, params=None, headers=None, response_class=None, retry_401=True
    ):
        """
        Make a GET request to the specified path.

        See :meth:`_request <._request>` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"GET to {path} with params {params}")
        return self._request(
            "GET",
            path,
            params=params,
            headers=headers,
            response_class=response_class,
            retry_401=retry_401,
        )

    def post(
        self,
        path,
        *,
        params=None,
        data=None,
        headers=None,
        encoding: typing.Optional[str] = None,
        response_class=None,
        retry_401=True,
    ):
        """
        Make a POST request to the specified path.

        See :meth:`_request <._request>` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"POST to {path} with params {params}")
        return self._request(
            "POST",
            path,
            params=params,
            data=data,
            headers=headers,
            encoding=encoding,
            response_class=response_class,
            retry_401=retry_401,
        )

    def delete(
        self, path, *, params=None, headers=None, response_class=None, retry_401=True
    ):
        """
        Make a DELETE request to the specified path.

        See :meth:`_request <._request>` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"DELETE to {path} with params {params}")
        return self._request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            response_class=response_class,
            retry_401=retry_401,
        )

    def put(
        self,
        path,
        *,
        params=None,
        data=None,
        headers=None,
        encoding: typing.Optional[str] = None,
        response_class=None,
        retry_401=True,
    ):
        """
        Make a PUT request to the specified path.

        See :meth:`_request <._request>` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"PUT to {path} with params {params}")
        return self._request(
            "PUT",
            path,
            params=params,
            data=data,
            headers=headers,
            encoding=encoding,
            response_class=response_class,
            retry_401=retry_401,
        )

    def patch(
        self,
        path,
        *,
        params=None,
        data=None,
        headers=None,
        encoding: typing.Optional[str] = None,
        response_class=None,
        retry_401=True,
    ):
        """
        Make a PATCH request to the specified path.

        See :meth:`_request <._request>` for details on the various parameters.

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        log.debug(f"PATCH to {path} with params {params}")
        return self._request(
            "PATCH",
            path,
            params=params,
            data=data,
            headers=headers,
            encoding=encoding,
            response_class=response_class,
            retry_401=retry_401,
        )

    def _request(
        self,
        method,
        path,
        *,
        params=None,
        data=None,
        headers=None,
        encoding: typing.Optional[str] = None,
        response_class=None,
        retry_401=True,
    ):
        """
        Send an HTTP request

        :param method: HTTP request method, as an all caps string
        :type method: str
        :param path: Path for the request, with or without leading slash
        :type path: str
        :param params: Parameters to be encoded as a query string
        :type params: dict
        :param headers: HTTP headers to add to the request
        :type headers: dict
        :param data: Data to send as the request body. May pass through encoding.
        :type data: dict or string
        :param encoding: A way to encode request data. "json", "form", and "text"
            are all valid values. Custom encodings can be used only if they are
            registered with the transport. By default, strings get "text" behavior and
            all other objects get "json".
        :type encoding: string
        :param response_class: Class for response object, overrides the client's
            ``default_response_class``
        :type response_class: class
        :param retry_401: Retry on 401 responses with fresh Authorization if
            ``self.authorizer`` supports it
        :type retry_401: bool

        :return: :class:`GlobusHTTPResponse \
        <globus_sdk.response.GlobusHTTPResponse>` object
        """
        # copy if present
        rheaders = {**headers} if headers else {}

        # add Authorization header, or (if it's a NullAuthorizer) possibly
        # explicitly remove the Authorization header
        if self.authorizer is not None:
            log.debug(
                "request will have authorization of type {}".format(
                    type(self.authorizer)
                )
            )
            self.authorizer.set_authorization_header(rheaders)

        # if a client is asked to make a request against a full URL, not just the path
        # component, then do not resolve the path, simply pass it through as the URL
        if path.startswith("https://") or path.startswith("http://"):
            url = path
        else:
            url = utils.slash_join(self.base_url, path)
        log.debug(f"request will hit URL:{url}")

        # initial request
        r = self._transport.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=rheaders,
            encoding=encoding,
        )

        log.debug(f"Request made to URL: {r.url}")

        # potential 401 retry handling
        if r.status_code == 401 and retry_401 and self.authorizer is not None:
            log.debug("request got 401, checking retry-capability")
            # note that although handle_missing_authorization returns a T/F
            # value, it may actually mutate the state of the authorizer and
            # therefore change the value set by the `set_authorization_header`
            # method
            if self.authorizer.handle_missing_authorization():
                log.debug("request can be retried")
                self.authorizer.set_authorization_header(rheaders)
                r = self._transport.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    headers=rheaders,
                    encoding=encoding,
                )

        if 200 <= r.status_code < 400:
            log.debug(f"request completed with response code: {r.status_code}")
            if response_class is None:
                return self.default_response_class(r, client=self)
            else:
                return response_class(r, client=self)

        log.debug(f"request completed with (error) response code: {r.status_code}")
        raise self.error_class(r)
