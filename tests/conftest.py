import pytest
import httpretty


@pytest.fixture(autouse=True)
def enable_httpretty():
    """
    All tests enable HTTPretty patching of the python socket module, replacing
    all network IO.
    """
    httpretty.enable()

    yield

    httpretty.disable()
    httpretty.reset()
