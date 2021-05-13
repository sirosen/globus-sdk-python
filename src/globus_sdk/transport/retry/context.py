import typing

import requests

from globus_sdk.authorizers import GlobusAuthorizer


class RetryContext:
    def __init__(
        self,
        attempt: int,
        *,
        retry_state: typing.Dict,
        response: typing.Optional[requests.Response] = None,
        exception: typing.Optional[Exception] = None,
        authorizer: typing.Optional[GlobusAuthorizer] = None,
    ):
        # retry attempt number
        self.attempt = attempt
        # the response or exception from a request
        # we expect exactly one of these to be non-null
        self.response = response
        self.exception = exception
        # the authorizer object (which may or may not be able to handle reauth)
        self.authorizer = authorizer
        # state which may be accumulated over multiple retry/retry-checker invocations
        # this is passed forward through all checkers and should be maintained outside
        # of the context of any singular retry
        self.retry_state: typing.Dict = retry_state or {}
