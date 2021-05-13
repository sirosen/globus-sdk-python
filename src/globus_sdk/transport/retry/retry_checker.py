import abc
import typing

import requests

from .context import RetryContext


class RetryChecker(metaclass=abc.ABCMeta):
    """
    A retry checker is responsible for implementing
    `should_retry(RetryContext) -> Union[float, bool, None]`

    `should_retry` should *not* perform any sleeps or delays, and should not mutate
    state. Multiple RetryChecker objects should be chainable, as part of a RetryPolicy.

    `should_retry -> True` means "retry this request"
    `should_retry -> False` means "do not retry"
    `should_retry -> None` means "no determination, ask other retry checkers"
    `should_retry -> float` means "delay this long, then retry"
    """

    @abc.abstractmethod
    def should_retry(self, context: RetryContext) -> typing.Union[float, bool, None]:
        raise NotImplementedError


class MaxRetriesRetryChecker(RetryChecker):
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries

    def should_retry(self, context):
        # max retries exceeded? don't retry
        if context.attempt > self.max_retries:
            return False


class StandardExceptionRetryChecker(RetryChecker):
    def should_retry(self, context):
        if context.exception:
            if isinstance(context.exception, requests.RequestException):
                return True
            return False


class RetryAfterRetryChecker(RetryChecker):
    # HTTP errors which may carry a Retry-After header
    STATUS_CODES = (429, 503)

    @staticmethod
    def _parse_retry_after(response: requests.Response) -> typing.Optional[int]:
        val = response.headers.get("Retry-After")
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def should_retry(self, context):
        if not context.response:
            return None
        if context.response.status_code in self.STATUS_CODES:
            retry_after = self._parse_retry_after(context.response)
            if retry_after:
                return retry_after
            return True


class TransientErrorRetryChecker(RetryChecker):
    # HTTP errors which may resolve after retries in normal conditions
    STATUS_CODES = (429, 500, 502, 503, 504)

    def should_retry(self, context):
        if not context.response:
            return None
        if context.response.status_code in self.STATUS_CODES:
            return True
