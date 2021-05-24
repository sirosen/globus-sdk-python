import typing

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
    # the retry policy may enforce a lower maximum, but this sets a hard cap to avoid
    # potential infinite loop with a bad policy
    max_retries: int = 20
    encoders: typing.Dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }

    BASE_USER_AGENT = f"globus-sdk-py-{__version__}"

    def __init__(
        self,
        verify_ssl: typing.Optional[bool] = None,
        http_timeout: typing.Optional[float] = None,
        retry_policy: typing.Optional[RetryPolicy] = None,
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
        params: typing.Optional[typing.Dict] = None,
        data: typing.Union[typing.Dict, typing.List, str, None] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        encoding: typing.Optional[str] = None,
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
        encoding: typing.Optional[str] = None,
        authorizer: typing.Optional[GlobusAuthorizer] = None,
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
        resp: typing.Optional[requests.Response] = None
        retry_state: typing.Dict = {}
        req = self._encode(method, url, params, data, headers, encoding)
        for attempt in range(self.max_retries):
            # add Authorization header, or (if it's a NullAuthorizer) possibly
            # explicitly remove the Authorization header
            # done fresh for each request, to handle potential for refreshed credentials
            if authorizer:
                authorizer.set_authorization_header(req.headers)

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
        if not resp:
            raise ValueError("Somehow, retries ended without a response")
        return resp
