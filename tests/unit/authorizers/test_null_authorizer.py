from globus_sdk.authorizers import NullAuthorizer


def test_get_authorization_header():
    """
    Gets authorization header. Confirms None value.
    """
    authorizer = NullAuthorizer()
    assert authorizer.get_authorization_header() is None


def test_handle_missing_authorization():
    """
    Confirms that NullAuthorizer doesn't handle missing authorization
    """
    authorizer = NullAuthorizer()
    assert not authorizer.handle_missing_authorization()
