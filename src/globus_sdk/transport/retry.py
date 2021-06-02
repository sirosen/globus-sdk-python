import enum
import random
import time
from typing import Callable, Dict, List, Optional, cast

import requests

from globus_sdk.authorizers import GlobusAuthorizer


class RetryCheckResult(enum.Enum):
    # yes, retry the request
    do_retry = enum.auto()
    # no, do not retry the request
    do_not_retry = enum.auto()
    # "I don't know", ask other checks for an answer
    no_decision = enum.auto()


class RetryContext:
    """
    The RetryContext is an object passed to retry checks in order to determine whether
    or not a request should be retried. The context is constructed after each request,
    regardless of success or failure.

    If an exception was raised, the context will contain that exception object.
    Otherwise, the context will contain a response object. Exactly one of ``response``
    or ``exception`` will be present.

    :param attempt: The request attempt number, starting at 0.
    :type attempt: int
    :param response: The response on a successful request
    :type response: requests.Response
    :param exception: The error raised when trying to send the request
    :type exception: Exception
    :param authorizer: The authorizer object from the client making the request
    :type authorizer: :class:`GlobusAuthorizer \
        <globus_sdk.authorizers.GlobusAuthorizer>`
    """

    def __init__(
        self,
        attempt: int,
        *,
        retry_state: Dict,
        response: Optional[requests.Response] = None,
        exception: Optional[Exception] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
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
        self.backoff: Optional[float] = None


def _parse_retry_after(response: requests.Response) -> Optional[int]:
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
    return cast(float, (0.25 + 0.5 * random.random()) * (2 ** ctx.attempt))


# type var useful for declaring RetryPolicy
RetryCheck = Callable[[RetryContext], RetryCheckResult]


class RetryPolicy:
    """
    The RetryPolicy object defines how retries are evaluated after a request.
    It defines several default hooks which are executed after every request, and
    additional hooks can be registered. The job of the RetryPolicy is to pass hooks
    a RetryContext to evaluate. Once a hook has determined that the request should or
    should not be retried, or all hooks have been consulted, the policy returns a
    result.

    The RetryPolicy is also responsible for determining the amount of backoff between
    retries, and executing the sleeps between retries itself.

    :param backoff: A function which determines how long to sleep between calls based on
        the RetryContext. Defaults to expontential backoff with jitter based on the
        context ``attempt`` number.
    :type backoff: callable
    :param checks: A list of initial checks for the policy. Any hooks registered,
        including the default hooks, will run after these checks.
    :type checks: list of callables
    :param max_sleep: The maximum sleep time between retries (in seconds). If the
        computed sleep time or the backoff requested by a retry check exceeds this
        value, this amount of time will be used instead
    :type max_sleep: int
    :param max_retries: The maximum number of retries allowed by this policy. This is
        checked by ``default_check_max_retries_exceeded`` to see if a request should
        stop retrying.
    :type max_retries: int
    """

    #: status codes for responses which may have a Retry-After header
    RETRY_AFTER_STATUS_CODES = (429, 503)
    #: status codes for error responses which should generally be retried
    TRANSIENT_ERROR_STATUS_CODES = (429, 500, 502, 503, 504)
    #: status codes indicating that authorization info was missing or expired
    EXPIRED_AUTHORIZATION_STATUS_CODES = (401,)

    def __init__(
        self,
        *,
        backoff: Callable[[RetryContext], float] = _exponential_backoff,
        checks: Optional[List[RetryCheck]] = None,
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
        """
        Given a retry context, compute the amount of time to sleep.
        This is always the minimum of the backoff (run on the context) and the
        ``max_sleep``.
        """
        return min(self.backoff(ctx), self.max_sleep)

    def should_retry(self, context: RetryContext) -> bool:
        """
        Determine whether or not a request should retry by consulting all registered
        checks.
        """
        for check in self.checks:
            result = check(context)
            if result is RetryCheckResult.no_decision:
                continue
            elif result is RetryCheckResult.do_not_retry:
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
        `check(RetryContext) -> RetryCheckResult`

        `check` should *not* perform any sleeps or delays.
        Multiple checks should be chainable, as part of a RetryPolicy.
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

    def default_check_max_retries_exceeded(self, ctx: RetryContext) -> RetryCheckResult:
        """check if the max retries for this policy have been exceeded"""
        return (
            RetryCheckResult.do_not_retry
            if ctx.attempt >= self.max_retries
            else RetryCheckResult.no_decision
        )

    def default_check_request_exception(self, ctx: RetryContext) -> RetryCheckResult:
        """check if a network error was encountered"""
        if ctx.exception and isinstance(ctx.exception, requests.RequestException):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    def default_check_retry_after_header(self, ctx: RetryContext) -> RetryCheckResult:
        """check for a retry-after header if the response had a matching status"""
        if (
            ctx.response is None
            or ctx.response.status_code not in self.RETRY_AFTER_STATUS_CODES
        ):
            return RetryCheckResult.no_decision
        retry_after = _parse_retry_after(ctx.response)
        if retry_after:
            ctx.backoff = float(retry_after)
        return RetryCheckResult.do_retry

    def default_check_transient_error(self, ctx: RetryContext) -> RetryCheckResult:
        """check for transient error status codes which could be resolved by retrying
        the request"""
        if ctx.response is not None and (
            ctx.response.status_code in self.TRANSIENT_ERROR_STATUS_CODES
        ):
            return RetryCheckResult.do_retry
        return RetryCheckResult.no_decision

    def default_check_expired_authorization(
        self, ctx: RetryContext
    ) -> RetryCheckResult:
        """check for expired authorization, as represented by a 401 error when the
        authorizer supports handling for missing/invalid authorization"""
        if (  # is the current check applicable?
            ctx.response is None
            or ctx.response.status_code not in self.EXPIRED_AUTHORIZATION_STATUS_CODES
            or ctx.authorizer is None
        ):
            return RetryCheckResult.no_decision

        # if reauth has already been tried on the current request, other checks can do
        # things, but do not do authorizer-driven retries
        if ctx.retry_state.get("has_done_reauth"):
            return RetryCheckResult.no_decision

        # the response code was a 401 and there's already been at least one reauth
        # attempt
        # this could be `do_not_retry` instead, but that would mean that nobody else can
        # add 401-retries even when reauth didn't work
        if not ctx.authorizer.handle_missing_authorization():
            return RetryCheckResult.no_decision

        ctx.retry_state["has_done_reauth"] = True
        return RetryCheckResult.do_retry
