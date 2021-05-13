import typing

import requests


class RetryContext:
    def __init__(
        self,
        attempt: int,
        *,
        response: typing.Optional[requests.Response] = None,
        exception: typing.Optional[Exception] = None
    ):
        self.attempt = attempt
        self.response = response
        self.exception = exception
