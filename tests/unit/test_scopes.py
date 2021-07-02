import uuid

from globus_sdk.scopes import ScopeBuilder


def test_url_scope_string():
    sb = ScopeBuilder(str(uuid.UUID(int=0)))
    assert sb.url_scope_string("data_access") == (
        "https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000"
        "/data_access"
    )


def test_urn_scope_string():
    sb = ScopeBuilder("example.globus.org")
    assert (
        sb.urn_scope_string("scope") == "urn:globus:auth:scope:example.globus.org:scope"
    )
