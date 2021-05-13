import abc
import time
import typing

from .context import RetryContext
from .retry_checker import RetryChecker


class RetryPolicy(metaclass=abc.ABCMeta):
    def __init__(self, *, checkers: typing.List[RetryChecker]):
        self.checkers = checkers

    @abc.abstractmethod
    def compute_delay(
        self, context: RetryContext, delay: typing.Optional[float]
    ) -> float:
        raise NotImplementedError

    def should_retry(self, context: RetryContext) -> bool:
        for checker in self.checkers:
            result = checker.should_retry(context)
            if result is None:
                continue
            elif result is False:
                return False
            else:
                time.sleep(self.compute_delay(context, result))
                return True

        # fallthrough: don't retry any request which isn't marked for retry by the
        # policy
        return False


class ExponentialBackoffRetryPolicy(RetryPolicy):
    max_sleep: int = 10

    def compute_delay(
        self, context: RetryContext, delay: typing.Optional[float]
    ) -> float:
        if delay is not None:
            return min(delay, self.max_sleep)

        # (0.5s * 2^attempt) results in ~15s of total sleep for 5 retries
        # 2^0 + 2^1 + 2^2 + 2^3 + 2^4 = 31
        # note that additional time can be spent sending the request or waiting for
        # a reply
        return typing.cast(float, 0.5 * (2 ** context.attempt))
