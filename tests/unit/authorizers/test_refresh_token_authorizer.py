import pytest

from globus_sdk.authorizers import RefreshTokenAuthorizer

try:
    import mock
except ImportError:
    from unittest import mock


REFRESH_TOKEN = "refresh_token_1"
ACCESS_TOKEN = "access_token_1"
EXPIRES_AT = -1


@pytest.fixture
def response():
    r = mock.Mock()
    r.by_resource_server = {
        "rs1": {"expires_at_seconds": -1, "access_token": "access_token_2"}
    }
    return r


@pytest.fixture
def client(response):
    c = mock.Mock()
    c.oauth2_refresh_token = mock.Mock(return_value=response)
    return c


@pytest.fixture
def authorizer(client):
    return RefreshTokenAuthorizer(
        REFRESH_TOKEN, client, access_token=ACCESS_TOKEN, expires_at=EXPIRES_AT
    )


def test_get_token_response(authorizer, client, response):
    """
    Calls _get_token_response, confirms that the mock
    AuthClient is used and the known data was returned.
    """
    # get new_access_token
    res = authorizer._get_token_response()
    assert res == response
    # confirm mock ConfidentailAppAuthClient was used as expected
    client.oauth2_refresh_token.assert_called_once_with(REFRESH_TOKEN)


def test_multiple_resource_servers(authorizer, response):
    """
    Sets the mock ConfidentialAppAuthClient to return multiple resource
    servers. Confirms GlobusError is raised when _extract_token_data is
    called.
    """
    response.by_resource_server["rs2"] = {
        "expires_at_seconds": -1,
        "access_token": "access_token_3",
    }
    with pytest.raises(ValueError) as excinfo:
        authorizer._extract_token_data(response)
    assert "didn't return exactly one token" in str(excinfo.value)
