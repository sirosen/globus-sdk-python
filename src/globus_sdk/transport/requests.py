import typing

import requests

from globus_sdk import exc
from globus_sdk.transport.encoders import (
    FormRequestEncoder,
    JSONRequestEncoder,
    RequestEncoder,
)
from globus_sdk.transport.retry import (
    RetryContext,
    RetryPolicy,
    get_default_retry_policy,
)


class RequestsTransport:
    # the retry policy may enforce a lower maximum, but this sets a hard cap to avoid
    # potential infinite loop with a bad policy
    max_retries: int = 20
    encoders: typing.Dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }

    def __init__(
        self,
        user_agent: str,
        verify_ssl=True,
        http_timeout=60,
        retry_policy: typing.Optional[RetryPolicy] = None,
    ):
        self._session = requests.Session()
        self._verify_ssl = verify_ssl
        self.user_agent = user_agent
        self.http_timeout = http_timeout
        self.retry_policy = retry_policy if retry_policy else get_default_retry_policy()

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
    ):
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
        req = self._encode(method, url, params, data, headers, encoding)
        resp = None
        for attempt in range(self.max_retries):
            ctx = RetryContext(attempt)
            try:
                resp = ctx.response = self._session.send(
                    req.prepare(), timeout=self.http_timeout, verify=self._verify_ssl
                )
            except requests.RequestException as err:
                ctx.exception = err
                if not self.retry_policy.should_retry(ctx):
                    raise exc.convert_request_exception(err)
            else:
                if self.retry_policy.should_retry(ctx):
                    continue
                return resp
        if not resp:
            raise ValueError("Somehow, retries ended without a response")
        return resp
