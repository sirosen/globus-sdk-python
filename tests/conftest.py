from unittest import mock

import pytest
import responses

from globus_sdk.transport import RequestsTransport


@pytest.fixture(autouse=True)
def mocksleep():
    with mock.patch("time.sleep") as m:
        yield m


@pytest.fixture
def no_retry_transport():
    class NoRetryTransport(RequestsTransport):
        DEFAULT_MAX_RETRIES = 0

    return NoRetryTransport


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
