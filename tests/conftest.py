import pytest
import responses

from globus_sdk.transport import RetryPolicy


@pytest.fixture
def no_retry_policy():
    class NoRetryPolicy(RetryPolicy):
        def register_default_checks(self):
            pass

    return NoRetryPolicy()


@pytest.fixture(autouse=True)
def mocked_responses():
    """
    All tests enable `responses` patching of the `requests` package, replacing
    all HTTP calls.
    """
    responses.start()

    yield

    responses.stop()
    responses.reset()
