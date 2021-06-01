import pytest

from globus_sdk.authorizers import AccessTokenAuthorizer

TOKEN = "DUMMY_TOKEN"


@pytest.fixture
def authorizer():
    return AccessTokenAuthorizer(TOKEN)


def test_get_authorization_header(authorizer):
    """
    Get authorization header, confirms expected value
    """
    assert authorizer.get_authorization_header() == "Bearer " + TOKEN


def test_handle_missing_authorization(authorizer):
    """
    Confirms that AccessTokenAuthorizer doesnt handle missing authorization
    """
    assert not authorizer.handle_missing_authorization()
