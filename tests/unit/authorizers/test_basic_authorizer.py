# -*- coding: utf-8 -*-
import base64

import pytest
import six

from globus_sdk.authorizers import BasicAuthorizer

USERNAME = "testUser"
PASSWORD = "PASSWORD"


@pytest.fixture
def authorizer():
    return BasicAuthorizer(USERNAME, PASSWORD)


def test_set_authorization_header(authorizer):
    """
    Sets authorization header in a test dictionary, confirms expected value
    """
    header_dict = {}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"][:6] == "Basic "
    decoded = base64.b64decode(six.b(header_dict["Authorization"][6:])).decode("utf-8")
    assert decoded == "{}:{}".format(USERNAME, PASSWORD)


def test_set_authorization_header_existing(authorizer):
    """
    Confirms that an existing Authorization field is overwritten
    """
    header_dict = {"Header": "value", "Authorization": "previous_value"}
    authorizer.set_authorization_header(header_dict)
    assert header_dict["Authorization"][:6] == "Basic "
    decoded = base64.b64decode(six.b(header_dict["Authorization"][6:])).decode("utf-8")
    assert decoded == "{}:{}".format(USERNAME, PASSWORD)
    assert header_dict["Header"] == "value"


def test_handle_missing_authorization(authorizer):
    """
    Confirms that BasicAuthorizer doesn't handle missing authorization
    """
    assert not authorizer.handle_missing_authorization()


@pytest.mark.parametrize(
    "username, password", [("user", u"テスト"), (u"дум", "pass"), (u"テスト", u"дум")]
)
def test_unicode_handling(username, password):
    """
    With a unicode string for the password, set and verify the
    Authorization header.
    """
    header_dict = {}
    authorizer = BasicAuthorizer(username, password)
    authorizer.set_authorization_header(header_dict)

    assert header_dict["Authorization"][:6] == "Basic "
    decoded = base64.b64decode(six.b(header_dict["Authorization"][6:])).decode("utf-8")
    assert decoded == u"{}:{}".format(username, password)
