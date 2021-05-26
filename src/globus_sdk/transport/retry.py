import random
import time
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
        self.retry_state = retry_state
        # the retry delay or "backoff" before retrying
        self.backoff: typing.Optional[float] = None


def _parse_retry_after(response: requests.Response) -> typing.Optional[int]:
    val = response.headers.get("Retry-After")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def _exponential_backoff(ctx: RetryContext) -> float:
    # respect any explicit backoff set on the context
    if ctx.backoff is not None:
        return ctx.backoff
    # expontential backoff with jitter
    return typing.cast(float, (0.25 + 0.5 * random.random()) * (2 ** ctx.attempt))


# type var useful for declaring RetryPolicy
RetryCheck = typing.Callable[[RetryContext], typing.Optional[bool]]


class RetryPolicy:
    RETRY_AFTER_STATUS_CODES = (429, 503)
    TRANSIENT_ERROR_STATUS_CODES = (429, 500, 502, 503, 504)
    EXPIRED_AUTHORIZATION_STATUS_CODES = (401,)

    def __init__(
        self,
        *,
        backoff: typing.Callable[[RetryContext], float] = _exponential_backoff,
        checks: typing.Optional[typing.List[RetryCheck]] = None,
        max_sleep: int = 10,
        max_retries: int = 5,
    ):
        self.backoff = backoff
        self.max_sleep = max_sleep
        self.max_retries = max_retries
        # copy
        self.checks = list(checks if checks else [])
        # register internal checks
        self.register_default_checks()

    def compute_delay(self, ctx: RetryContext) -> float:
        delay = self.backoff(ctx)
        return min(delay, self.max_sleep)

    def should_retry(self, context: RetryContext) -> bool:
        for check in self.checks:
            result = check(context)
            if result is None:
                continue
            elif result is False:
                return False
            else:
                time.sleep(self.compute_delay(context))
                return True

        # fallthrough: don't retry any request which isn't marked for retry by the
        # policy
        return False

    # decorator which lets you add a check to a retry policy
    def register_check(self, func: RetryCheck) -> RetryCheck:
        """
        A retry checker is a callable responsible for implementing
        `check(RetryContext) -> Optional[bool]`

        `check` should *not* perform any sleeps or delays.
        Multiple checks should be chainable, as part of a RetryPolicy.

        `check() -> True` means "retry this request"
        `check() -> False` means "do not retry"
        `check() -> None` means "no determination, ask other retry checkers"
        """
        self.checks.append(func)
        return func

    def register_default_checks(self):
        """
        This hook is called during RetryPolicy initialization. By default, it registers
        the following hooks:
          - default_check_max_retries_exceeded
          - default_check_request_exception
          - default_check_retry_after_header
          - default_check_tranisent_error
          - default_check_expired_authorization

        It can be overridden to register additional hooks or to remove the default
        hooks.
        """
        self.register_check(self.default_check_max_retries_exceeded)
        self.register_check(self.default_check_request_exception)
        self.register_check(self.default_check_retry_after_header)
        self.register_check(self.default_check_transient_error)
        self.register_check(self.default_check_expired_authorization)

    def default_check_max_retries_exceeded(
        self, ctx: RetryContext
    ) -> typing.Optional[bool]:
        # max retries exceeded? don't retry
        return False if ctx.attempt >= self.max_retries else None

    def default_check_request_exception(
        self, ctx: RetryContext
    ) -> typing.Optional[bool]:
        if not ctx.exception:
            return None
        return isinstance(ctx.exception, requests.RequestException)

    def default_check_retry_after_header(
        self, ctx: RetryContext
    ) -> typing.Optional[bool]:
        if (
            ctx.response is None
            or ctx.response.status_code not in self.RETRY_AFTER_STATUS_CODES
        ):
            return None
        retry_after = _parse_retry_after(ctx.response)
        if retry_after:
            ctx.backoff = float(retry_after)
        return True

    def default_check_transient_error(self, ctx: RetryContext) -> typing.Optional[bool]:
        if (
            ctx.response is None
            or ctx.response.status_code not in self.TRANSIENT_ERROR_STATUS_CODES
        ):
            return None
        return True

    def default_check_expired_authorization(
        self, ctx: RetryContext
    ) -> typing.Optional[bool]:
        if ctx.response is None:
            return None
        if ctx.response.status_code not in self.EXPIRED_AUTHORIZATION_STATUS_CODES:
            return None
        if ctx.authorizer is None:
            return None
        # the response code was a 401 and there's already been at least one reauth
        # attempt
        # this could be `False` instead, but that would mean that nobody else can add
        # 401-retries even when reauth didn't work
        if ctx.retry_state.get("has_done_reauth"):
            return None

        if not ctx.authorizer.handle_missing_authorization():
            return None

        ctx.retry_state["has_done_reauth"] = True
        return True
