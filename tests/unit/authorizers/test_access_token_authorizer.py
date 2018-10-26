import pytest

from globus_sdk.authorizers import AccessTokenAuthorizer

TOKEN = "DUMMY_TOKEN"


@pytest.fixture
def authorizer():
    return AccessTokenAuthorizer(TOKEN)


def test_set_authorization_header(authorizer):
    """
    Sets authorization header in a test dictionary, confirms expected value
    """
    header_dict = {}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == "Bearer " + TOKEN


def test_set_authorization_header_existing(authorizer):
    """
    Confirms that an existing Authorization field is overwritten
    """
    header_dict = {"Header": "value", "Authorization": "previous_value"}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"] == "Bearer " + TOKEN
    assert header_dict["Header"] == "value"


def test_handle_missing_authorization(authorizer):
    """
    Confirms that AccessTokenAuthorizer doesnt handle missing authorization
    """
    assert not authorizer.handle_missing_authorization()
