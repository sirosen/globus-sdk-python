from unittest import mock

import pytest

from globus_sdk.transport import RetryCheckResult, RetryContext, RetryPolicy


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_respects_retry_after(mocksleep, http_status):
    policy = RetryPolicy()

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "5"}
    dummy_response.status_code = http_status
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    assert policy.should_retry(ctx) is True
    mocksleep.assert_called_once_with(5)


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_ignores_retry_after_too_high(mocksleep, http_status):
    # set explicit max sleep to confirm that the value is capped here
    policy = RetryPolicy(max_sleep=5)

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "20"}
    dummy_response.status_code = http_status
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    assert policy.should_retry(ctx) is True
    mocksleep.assert_called_once_with(5)


@pytest.mark.parametrize("http_status", (429, 503))
def test_retry_policy_ignores_malformed_retry_after(mocksleep, http_status):
    policy = RetryPolicy()

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "not-an-integer"}
    dummy_response.status_code = http_status
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    assert policy.should_retry(ctx) is True
    mocksleep.assert_called_once()


@pytest.mark.parametrize(
    "checkname",
    [
        "default_check_retry_after_header",
        "default_check_transient_error",
        "default_check_expired_authorization",
    ],
)
def test_default_retry_check_noop_on_exception(checkname, mocksleep):
    policy = RetryPolicy()
    method = getattr(policy, checkname)
    ctx = RetryContext(1, retry_state={}, exception=Exception("foo"))
    assert method(ctx) is RetryCheckResult.no_decision
