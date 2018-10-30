from globus_sdk.authorizers import NullAuthorizer


def test_set_authorization_header():
    """
    Sets authorization header in a test dictionary,
    Confirms that nothing happens.
    and any existing Authorization header is removed
    """
    header_dict = {}
    authorizer = NullAuthorizer()
    authorizer.set_authorization_header(header_dict)
    assert header_dict == {}


def test_set_authorization_header_existing():
    """
    Confirms that an existing Authorization field is removed
    """
    header_dict = {"Header": "value", "Authorization": "previous_value"}
    authorizer = NullAuthorizer()
    authorizer.set_authorization_header(header_dict)
    assert header_dict == {"Header": "value"}


def test_handle_missing_authorization():
    """
    Confirms that NullAuthorizer doesn't handle missing authorization
    """
    authorizer = NullAuthorizer()
    assert not authorizer.handle_missing_authorization()
