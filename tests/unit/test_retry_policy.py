from unittest import mock

import pytest

from globus_sdk.transport import RetryContext, RetryPolicy


def test_retry_policy_respects_retry_after():
    policy = RetryPolicy()

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "5"}
    dummy_response.status_code = 429
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    with mock.patch("time.sleep") as mocksleep:
        assert policy.should_retry(ctx) is True

        mocksleep.assert_called_once_with(5)


def test_retry_policy_ignores_retry_after_too_high():
    # set explicit max sleep to confirm that the value is capped here
    policy = RetryPolicy(max_sleep=5)

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "20"}
    dummy_response.status_code = 429
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    with mock.patch("time.sleep") as mocksleep:
        assert policy.should_retry(ctx) is True

        mocksleep.assert_called_once_with(5)


def test_retry_policy_ignores_malformed_retry_after():
    policy = RetryPolicy()

    dummy_response = mock.Mock()
    dummy_response.headers = {"Retry-After": "not-an-integer"}
    dummy_response.status_code = 429
    ctx = RetryContext(1, retry_state={}, response=dummy_response)

    with mock.patch("time.sleep") as mocksleep:
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
def test_default_retry_check_noop_on_exception(checkname):
    policy = RetryPolicy()
    method = getattr(policy, checkname)
    ctx = RetryContext(1, retry_state={}, exception=Exception("foo"))
    assert method(ctx) is None
