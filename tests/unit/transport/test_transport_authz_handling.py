from unittest import mock

from globus_sdk.authorizers import NullAuthorizer
from globus_sdk.transport import RequestsTransport


def test_will_not_modify_authz_header_without_authorizer():
    request = mock.Mock()
    request.headers = {}

    transport = RequestsTransport()
    transport._set_authz_header(None, request)
    assert request.headers == {}

    request.headers["Authorization"] = "foo bar"
    transport._set_authz_header(None, request)
    assert request.headers == {"Authorization": "foo bar"}


def test_will_null_authz_header_with_null_authorizer():
    request = mock.Mock()
    request.headers = {}

    transport = RequestsTransport()
    transport._set_authz_header(NullAuthorizer(), request)
    assert request.headers == {}

    request.headers["Authorization"] = "foo bar"
    transport._set_authz_header(NullAuthorizer(), request)
    assert request.headers == {}
