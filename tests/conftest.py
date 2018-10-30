import httpretty
import pytest

# disable the use of real sockets when HTTPretty socket mocking is in place --
# if you make a real API call, it will immediately error
httpretty.httpretty.allow_net_connect = False


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
