import time

import pytest

from globus_sdk.authorizers.renewing import EXPIRES_ADJUST_SECONDS, RenewingAuthorizer

try:
    import mock
except ImportError:
    from unittest import mock


class MockRenewer(RenewingAuthorizer):
    """
    Class that implements RenewingAuthorizer so that _get_token_response and
    _extract_token_data can return known values for testing
    """

    def __init__(self, token_data, **kwargs):
        self.token_data = token_data
        self.token_response = mock.Mock()
        super(MockRenewer, self).__init__(**kwargs)

    def _get_token_response(self):
        return self.token_response

    def _extract_token_data(self, res):
        return self.token_data


ACCESS_TOKEN = "access_token_1"


@pytest.fixture
def expires_at():
    return int(time.time()) + EXPIRES_ADJUST_SECONDS + 1


@pytest.fixture
def token_data():
    return {
        "expires_at_seconds": int(time.time()) + 1000,
        "access_token": "access_token_2",
    }


@pytest.fixture
def on_refresh():
    return mock.Mock()


@pytest.fixture
def authorizer(on_refresh, token_data, expires_at):
    return MockRenewer(
        token_data,
        access_token=ACCESS_TOKEN,
        expires_at=expires_at,
        on_refresh=on_refresh,
    )


@pytest.fixture
def expired_authorizer(on_refresh, token_data, expires_at):
    return MockRenewer(
        token_data,
        access_token=ACCESS_TOKEN,
        expires_at=expires_at - 1,
        on_refresh=on_refresh,
    )


def test_init(token_data, expires_at):
    """
    Creating a MockRenewer with partial data results in a new access token
    being fetched, but complete data does not
    """
    authorizer = MockRenewer(
        token_data, access_token=ACCESS_TOKEN, expires_at=expires_at
    )
    assert authorizer.access_token == ACCESS_TOKEN
    assert authorizer.access_token != token_data["access_token"]

    authorizer = MockRenewer(token_data, access_token=ACCESS_TOKEN)
    assert authorizer.access_token != ACCESS_TOKEN
    assert authorizer.access_token == token_data["access_token"]

    authorizer = MockRenewer(token_data, expires_at=expires_at)
    assert authorizer.access_token != ACCESS_TOKEN
    assert authorizer.access_token == token_data["access_token"]


def test_init_expiration_time(authorizer, expires_at):
    # confirm initial value was adjusted automatically
    assert authorizer.expires_at == expires_at - EXPIRES_ADJUST_SECONDS


@pytest.mark.parametrize("input_time", [0, 60, 120, 1200])
def test_set_expiration_time(input_time, authorizer, expires_at):
    """
    Confirms expiration time is set earlier than input value for a buffer
    """
    authorizer._set_expiration_time(input_time)
    assert authorizer.expires_at == input_time - EXPIRES_ADJUST_SECONDS


def test_get_new_access_token(authorizer, token_data, on_refresh):
    """
    Calls get_new_acces token, confirms that the mock _get_token_data
    is used and that the mock on_refresh function is called.
    """
    # take note of original access_token_hash
    original_hash = authorizer.access_token_hash

    # get new_access_token
    authorizer._get_new_access_token()
    # confirm side effects
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == (
        token_data["expires_at_seconds"] - EXPIRES_ADJUST_SECONDS
    )
    assert authorizer.access_token_hash != original_hash
    on_refresh.assert_called_once()


def test_check_expiration_time_valid(authorizer):
    """
    Confirms nothing is done before the access_token expires,
    """
    authorizer.check_expiration_time()
    assert authorizer.access_token == ACCESS_TOKEN


def test_check_expiration_time_expired(expired_authorizer, token_data):
    """
    Confirms a new access_token is gotten after expiration
    """
    expired_authorizer.check_expiration_time()
    assert expired_authorizer.access_token == token_data["access_token"]
    assert expired_authorizer.expires_at == (
        token_data["expires_at_seconds"] - EXPIRES_ADJUST_SECONDS
    )


def test_check_expiration_time_no_token(authorizer, token_data):
    """
    Confirms a new access_token is gotten if the old one is set to None
    """
    authorizer.access_token = None
    authorizer.check_expiration_time()
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == (
        token_data["expires_at_seconds"] - EXPIRES_ADJUST_SECONDS
    )


def test_check_expiration_time_no_expiration(authorizer, token_data):
    """
    Confirms a new access_token is gotten if expires_at is set to None
    """
    authorizer.expires_at = None
    authorizer.check_expiration_time()
    assert authorizer.access_token == token_data["access_token"]
    assert authorizer.expires_at == (
        token_data["expires_at_seconds"] - EXPIRES_ADJUST_SECONDS
    )


def test_set_authorization_header(authorizer):
    """
    Sets authorization header on a test dictionary, confirms expected value
    """
    header_dict = {}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == "Bearer " + ACCESS_TOKEN


def test_set_authorization_header_existing(authorizer):
    """
    Confirms that an existing Authorization field is overwritten
    """
    header_dict = {"Header": "value", "Authorization": "previous_value"}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == "Bearer " + ACCESS_TOKEN
    assert header_dict["Header"] == "value"


def test_set_authorization_header_expired(expired_authorizer, token_data):
    """
    Sets the access_token to be expired, then sets authorization header
    Confirms header value uses the new access_token.
    """
    header_dict = {}

    expired_authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == ("Bearer " + token_data["access_token"])


def test_set_authorization_header_no_token(authorizer, token_data):
    """
    Sets the access_token to None, then sets authorization header
    Confirms header value uses the new access_token.
    """
    header_dict = {}
    authorizer.access_token = None

    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == ("Bearer " + token_data["access_token"])


def test_set_authorization_header_no_expires(authorizer, token_data):
    """
    Sets expires_at to None, then sets authorization header
    Confirms header value uses the new access_token.
    """
    header_dict = {}
    authorizer.expires_at = None

    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == ("Bearer " + token_data["access_token"])


def test_handle_missing_authorization(authorizer):
    """
    Confirms that RenewingAuthorizers will attempt to fix 401s
    by treating their existing access_token as expired
    """
    assert authorizer.handle_missing_authorization()
    assert authorizer.expires_at is None
