import textwrap
import uuid

from globus_sdk.scopes import (
    ComputeScopes,
    DynamicScopeCollection,
    FlowsScopes,
    Scope,
    StaticScopeCollection,
)
from globus_sdk.scopes.collection import _url_scope, _urn_scope


def test_url_scope_string():
    resource_server = str(uuid.UUID(int=0))
    s = _url_scope(resource_server, "data_access")
    assert isinstance(s, Scope)
    assert str(s) == (
        "https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000"
        "/data_access"
    )


def test_urn_scope_string():
    resource_server = "example.globus.org"
    s = _urn_scope(resource_server, "myscope")
    assert isinstance(s, Scope)
    assert str(s) == "urn:globus:auth:scope:example.globus.org:myscope"


def test_static_scope_collection_str_contains_expected_values():
    class MyScopes(StaticScopeCollection):
        resource_server = str(uuid.UUID(int=0))

        foo = _urn_scope(resource_server, "foo")
        bar = _url_scope(resource_server, "bar")

    stringified = str(MyScopes)
    assert MyScopes.resource_server in stringified
    assert str(MyScopes.foo) in stringified
    assert str(MyScopes.bar) in stringified


def test_dynamic_scope_collection_contains_expected_values():
    class MyScopes(DynamicScopeCollection):
        _scope_names = ("foo", "bar")

        @property
        def foo(self):
            return _urn_scope(self.resource_server, "foo")

        @property
        def bar(self):
            return _url_scope(self.resource_server, "bar")

    resource_server = str(uuid.UUID(int=10))
    scope_collection = MyScopes(resource_server)
    stringified = str(scope_collection)
    assert scope_collection.resource_server in stringified
    assert str(scope_collection.foo) in stringified
    assert str(scope_collection.bar) in stringified


def test_flows_scopes_creation():
    assert FlowsScopes.resource_server == "flows.globus.org"
    assert (
        str(FlowsScopes.run)
        == "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
    )


def test_compute_scopes_creation():
    assert ComputeScopes.resource_server == "funcx_service"
    assert (
        str(ComputeScopes.all)
        == "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all"
    )


def test_stringify_static_scope_collection():
    class MyScopes(StaticScopeCollection):
        resource_server = "foo"
        sc1 = _urn_scope(resource_server, "sc1")

    assert str(MyScopes) == textwrap.dedent(
        """\
        MyScopes[foo]
          sc1:
            urn:globus:auth:scope:foo:sc1"""
    )
