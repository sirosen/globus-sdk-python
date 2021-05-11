import typing

import requests

from globus_sdk import exc
from globus_sdk.transport.encoders import (
    FormRequestEncoder,
    JSONRequestEncoder,
    RequestEncoder,
)
from globus_sdk.transport.retry_policy import RetryPolicy


class RequestsTransport:
    encoders: typing.Dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }
    retry_policy = RetryPolicy()

    def __init__(self, user_agent: str, verify_ssl=True, http_timeout=60):
        self._session = requests.Session()
        self._verify_ssl = verify_ssl
        self.user_agent = user_agent
        self.http_timeout = http_timeout

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
        for attempt in range(self.retry_policy.max_retries):
            try:
                resp = self._session.send(
                    req.prepare(), timeout=self.http_timeout, verify=self._verify_ssl
                )
            except requests.RequestException as err:
                if not self.retry_policy.should_retry(attempt, err):
                    raise exc.convert_request_exception(err)
            else:
                if self.retry_policy.should_retry(attempt, resp):
                    continue
                return resp
        if not resp:
            raise ValueError(
                "Somehow, retries ended without a response. "
                "Possibly a bad retry policy."
            )
        return resp
