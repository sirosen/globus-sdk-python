from typing import Dict, List, Optional, Union

import requests

from globus_sdk import config, exc
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.transport.encoders import (
    FormRequestEncoder,
    JSONRequestEncoder,
    RequestEncoder,
)
from globus_sdk.transport.retry import RetryContext, RetryPolicy
from globus_sdk.version import __version__


class RequestsTransport:
    """
    The RequestsTransport handles HTTP request sending and retries.

    It receives raw request information from a client class, and then performs the
    following steps
    - encode the data in a prepared request
    - repeatedly send the request until no retry is requested by the retry policy
    - return the last response or reraise the last exception

    :param verify_ssl: Explicitly enable or disable SSL verification. This parameter
        defaults to True, but can be set via the ``GLOBUS_SDK_VERIFY_SSL`` environment
        variable. Any non-``None`` setting via this parameter takes precedence over the
        environment variable.
    :type verify_ssl: bool
    :param http_timeout: Explicitly set an HTTP timeout value in seconds. This parameter
        defaults to 60s but can be set via the ``GLOBUS_SDK_HTTP_TIMEOUT`` environment
        variable. Any value set via this parameter takes precedence over the environment
        variable.
    :type http_timeout: int
    """

    # the retry policy may enforce a lower maximum, but this sets a hard cap to avoid
    # potential infinite loop with a bad policy
    max_retries: int = 20

    #: the encoders are a mapping of encoding names to encoder objects
    encoders: Dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }

    BASE_USER_AGENT = f"globus-sdk-py-{__version__}"

    def __init__(
        self,
        verify_ssl: Optional[bool] = None,
        http_timeout: Optional[float] = None,
        retry_policy: Optional[RetryPolicy] = None,
    ):
        self.session = requests.Session()
        self.verify_ssl = config.get_ssl_verify(verify_ssl)
        self.http_timeout = config.get_http_timeout(http_timeout)
        self.retry_policy = retry_policy if retry_policy else RetryPolicy()
        self._user_agent = self.BASE_USER_AGENT

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value):
        self._user_agent = f"{self.BASE_USER_AGENT}/{value}"

    @property
    def _headers(self):
        return {"Accept": "application/json", "User-Agent": self.user_agent}

    def _encode(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Union[Dict, List, str, None] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
    ):
        if not headers:
            headers = {}
        headers = {**self._headers, **headers}

        if encoding is None:
            if isinstance(data, str):
                encoding = "text"
            else:
                encoding = "json"

        if encoding not in self.encoders:
            raise ValueError(
                f"Unknown encoding '{encoding}' is not supported by this transport."
            )

        return self.encoders[encoding].encode(method, url, params, data, headers)

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        encoding: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
    ) -> requests.Response:
        """
        Send an HTTP request

        :param url: URL for the request
        :type path: str
        :param method: HTTP request method, as an all caps string
        :type method: str
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

        :return: ``requests.Response`` object
        """
        resp: Optional[requests.Response] = None
        retry_state: Dict = {}
        req = self._encode(method, url, params, data, headers, encoding)
        for attempt in range(self.max_retries):
            # add Authorization header, or (if it's a NullAuthorizer) possibly
            # explicitly remove the Authorization header
            # done fresh for each request, to handle potential for refreshed credentials
            if authorizer:
                authz_header = authorizer.get_authorization_header()
                if authz_header:
                    req.headers["Authorization"] = authz_header
                else:
                    req.headers.pop("Authorization", None)  # remove any possible value

            ctx = RetryContext(attempt, authorizer=authorizer, retry_state=retry_state)
            try:
                resp = ctx.response = self.session.send(
                    req.prepare(), timeout=self.http_timeout, verify=self.verify_ssl
                )
            except requests.RequestException as err:
                ctx.exception = err
                if not self.retry_policy.should_retry(ctx):
                    raise exc.convert_request_exception(err)
            else:
                if not self.retry_policy.should_retry(ctx):
                    return resp
        if resp is None:
            raise ValueError("Somehow, retries ended without a response")
        return resp
