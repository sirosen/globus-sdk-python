import enum
import random
import time
from typing import Any, Callable, Dict, List, Optional, Union, cast

import requests

from globus_sdk import config, exc
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.transport.encoders import (
    FormRequestEncoder,
    JSONRequestEncoder,
    RequestEncoder,
)
from globus_sdk.version import __version__


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
        response: Optional[requests.Response] = None,
        exception: Optional[Exception] = None,
    ):
        # retry attempt number
        self.attempt = attempt
        # the response or exception from a request
        # we expect exactly one of these to be non-null
        self.response = response
        self.exception = exception
        # the retry delay or "backoff" before retrying
        self.backoff: Optional[float] = None


# type var useful for declaring RetryPolicy
RetryCheck = Callable[[RetryContext], RetryCheckResult]


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


class RequestsTransport:
    """
    The RequestsTransport handles HTTP request sending and retries.

    It receives raw request information from a client class, and then performs the
    following steps
    - encode the data in a prepared request
    - repeatedly send the request until no retry is requested
    - return the last response or reraise the last exception

    Retry checks are registered as hooks on the Transport. Additional hooks can be
    passed to the constructor via `retry_checks`. Or hooks can be added to an existing
    transport via a decorator.

    :param verify_ssl: Explicitly enable or disable SSL verification. This parameter
        defaults to True, but can be set via the ``GLOBUS_SDK_VERIFY_SSL`` environment
        variable. Any non-``None`` setting via this parameter takes precedence over the
        environment variable.
    :type verify_ssl: bool
    :param http_timeout: Explicitly set an HTTP timeout value in seconds. This parameter
        defaults to 60s but can be set via the ``GLOBUS_SDK_HTTP_TIMEOUT`` environment
        variable. Any value set via this parameter takes precedence over the environment
        variable.
    :type http_timeout: int
    :param retry_backoff: A function which determines how long to sleep between calls
        based on the RetryContext. Defaults to expontential backoff with jitter based on
        the context ``attempt`` number.
    :type retry_backoff: callable
    :param retry_checks: A list of initial checks for the policy. Any hooks registered,
        including the default hooks, will run after these checks.
    :type retry_checks: list of callables
    :param max_sleep: The maximum sleep time between retries (in seconds). If the
        computed sleep time or the backoff requested by a retry check exceeds this
        value, this amount of time will be used instead
    :type max_sleep: int
    :param max_retries: The maximum number of retries allowed by this policy. This is
        checked by ``default_check_max_retries_exceeded`` to see if a request should
        stop retrying.
    :type max_retries: int
    """

    #: default maximum number of retries
    DEFAULT_MAX_RETRIES = 5

    #: status codes for responses which may have a Retry-After header
    RETRY_AFTER_STATUS_CODES = (429, 503)
    #: status codes for error responses which should generally be retried
    TRANSIENT_ERROR_STATUS_CODES = (429, 500, 502, 503, 504)
    #: status codes indicating that authorization info was missing or expired
    EXPIRED_AUTHORIZATION_STATUS_CODES = (401,)

    #: the encoders are a mapping of encoding names to encoder objects
    encoders: Dict[str, RequestEncoder] = {
        "text": RequestEncoder(),
        "json": JSONRequestEncoder(),
        "form": FormRequestEncoder(),
    }

    BASE_USER_AGENT = f"globus-sdk-py-{__version__}"

    def __init__(
        self,
        verify_ssl: Optional[bool] = None,
        http_timeout: Optional[float] = None,
        retry_backoff: Callable[[RetryContext], float] = _exponential_backoff,
        retry_checks: Optional[List[RetryCheck]] = None,
        max_sleep: int = 10,
        max_retries: Optional[int] = None,
    ):
        self.session = requests.Session()
        self.verify_ssl = config.get_ssl_verify(verify_ssl)
        self.http_timeout = config.get_http_timeout(http_timeout)
        self._user_agent = self.BASE_USER_AGENT

        # retry parameters
        self.retry_backoff = retry_backoff
        self.max_sleep = max_sleep
        self.max_retries = (
            max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        )
        self.retry_checks = list(retry_checks if retry_checks else [])  # copy
        # register internal checks
        self.register_default_retry_checks()

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
        query_params: Optional[Dict[str, Any]] = None,
        data: Union[Dict, List, str, None] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
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

        return self.encoders[encoding].encode(method, url, query_params, data, headers)

    def request(
        self,
        method,
        url,
        query_params: Optional[Dict[str, Any]] = None,
        data=None,
        headers=None,
        encoding: Optional[str] = None,
        authorizer: Optional[GlobusAuthorizer] = None,
    ) -> requests.Response:
        """
        Send an HTTP request

        :param url: URL for the request
        :type path: str
        :param method: HTTP request method, as an all caps string
        :type method: str
        :param query_params: Parameters to be encoded as a query string
        :type query_params: dict, optional
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
        resp: Optional[requests.Response] = None
        req = self._encode(method, url, query_params, data, headers, encoding)
        has_done_reauth = False
        for attempt in range(self.max_retries + 1):
            # add Authorization header, or (if it's a NullAuthorizer) possibly
            # explicitly remove the Authorization header
            # done fresh for each request, to handle potential for refreshed credentials
            if authorizer:
                authz_header = authorizer.get_authorization_header()
                if authz_header:
                    req.headers["Authorization"] = authz_header
                else:
                    req.headers.pop("Authorization", None)  # remove any possible value

            ctx = RetryContext(attempt)
            try:
                resp = ctx.response = self.session.send(
                    req.prepare(), timeout=self.http_timeout, verify=self.verify_ssl
                )
            except requests.RequestException as err:
                ctx.exception = err
                if attempt >= self.max_retries or not self.should_retry(ctx):
                    raise exc.convert_request_exception(err)
            else:
                # check the expired authz handler, and if that doesn't work or has
                # already run on this request, turn to retry checks
                do_retry = False
                if not has_done_reauth and authorizer is not None:
                    do_retry = has_done_reauth = self.handle_expired_authorization(
                        authorizer, ctx
                    )
                do_retry = do_retry or self.should_retry(ctx)
                if not do_retry:
                    return resp

            # the request will be retried, so sleep...
            if attempt < self.max_retries:
                self._retry_sleep(ctx)
        if resp is None:
            raise ValueError("Somehow, retries ended without a response")
        return resp

    def _retry_sleep(self, ctx: RetryContext):
        """
        Given a retry context, compute the amount of time to sleep and sleep that much
        This is always the minimum of the backoff (run on the context) and the
        ``max_sleep``.
        """
        time.sleep(min(self.retry_backoff(ctx), self.max_sleep))

    def should_retry(self, context: RetryContext) -> bool:
        """
        Determine whether or not a request should retry by consulting all registered
        checks.
        """
        for check in self.retry_checks:
            result = check(context)
            if result is RetryCheckResult.no_decision:
                continue
            elif result is RetryCheckResult.do_not_retry:
                return False
            else:
                return True

        # fallthrough: don't retry any request which isn't marked for retry by the
        # policy
        return False

    def handle_expired_authorization(
        self, authorizer: GlobusAuthorizer, ctx: RetryContext
    ) -> bool:
        """
        This check and handler for expired authorization is handled outside of the
        retry checks.
        The reason is twofold:
        1. it may have side-effects on the authorizer
        2. it should only be run once per request if it makes changes
        """
        if (  # is the current check applicable?
            ctx.response is None
            or ctx.response.status_code not in self.EXPIRED_AUTHORIZATION_STATUS_CODES
        ):
            return False

        # run the authorizer's handler, and return True if the handler indicated that it
        # was able to make a change which should make the request retryable
        return cast(bool, authorizer.handle_missing_authorization())

    # decorator which lets you add a check to a retry policy
    def register_retry_check(self, func: RetryCheck) -> RetryCheck:
        """
        A retry checker is a callable responsible for implementing
        `check(RetryContext) -> RetryCheckResult`

        `check` should *not* perform any sleeps or delays.
        Multiple checks should be chainable.
        """
        self.retry_checks.append(func)
        return func

    def register_default_retry_checks(self):
        """
        This hook is called during transport initialization. By default, it registers
        the following hooks:

        - default_check_request_exception
        - default_check_retry_after_header
        - default_check_tranisent_error

        It can be overridden to register additional hooks or to remove the default
        hooks.
        """
        self.register_retry_check(self.default_check_request_exception)
        self.register_retry_check(self.default_check_retry_after_header)
        self.register_retry_check(self.default_check_transient_error)

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
