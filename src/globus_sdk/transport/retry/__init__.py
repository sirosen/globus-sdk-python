from .context import RetryContext
from .policy import ExponentialBackoffRetryPolicy, RetryPolicy
from .retry_checker import (
    ExpiredAuthorizationRetryChecker,
    MaxRetriesRetryChecker,
    RetryAfterRetryChecker,
    RetryChecker,
    StandardExceptionRetryChecker,
    TransientErrorRetryChecker,
)


def get_default_retry_policy():
    return ExponentialBackoffRetryPolicy(
        checkers=[
            MaxRetriesRetryChecker(),
            RetryAfterRetryChecker(),
            StandardExceptionRetryChecker(),
            TransientErrorRetryChecker(),
            ExpiredAuthorizationRetryChecker(),
        ]
    )


__all__ = (
    "RetryPolicy",
    "ExponentialBackoffRetryPolicy",
    "RetryChecker",
    "RetryContext",
    "get_default_retry_policy",
    "DEFAULT_NUM_RETRIES",
)
