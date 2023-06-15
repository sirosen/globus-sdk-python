import uuid

import pytest

from globus_sdk.scopes import FlowsScopes, MutableScope, ScopeBuilder


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


def test_known_scopes():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo")
    assert sb.foo == "urn:globus:auth:scope:00000000-0000-0000-0000-000000000000:foo"


def test_known_url_scopes():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_url_scopes="foo")
    assert sb.foo == (
        "https://auth.globus.org/scopes/00000000-0000-0000-0000-000000000000/foo"
    )


def test_scopebuilder_str():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo", known_url_scopes="bar")
    rs, foo_scope, bar_scope = sb.resource_server, sb.foo, sb.bar

    stringified = str(sb)
    assert rs in stringified
    assert foo_scope in stringified
    assert bar_scope in stringified


def test_uniquely_named_scopes():
    rs = str(uuid.uuid4())
    scope_1 = str(uuid.uuid4())
    scope_2 = str(uuid.uuid4())
    sb = ScopeBuilder(
        rs,
        known_scopes=[("my_urn_scope", scope_1), "foo"],
        known_url_scopes=[("my_url_scope", scope_2), "bar"],
    )

    assert sb.my_urn_scope == f"urn:globus:auth:scope:{rs}:{scope_1}"
    assert sb.foo == f"urn:globus:auth:scope:{rs}:foo"
    assert sb.my_url_scope == f"https://auth.globus.org/scopes/{rs}/{scope_2}"
    assert sb.bar == f"https://auth.globus.org/scopes/{rs}/bar"


def test_sb_allowed_inputs_types():
    rs = str(uuid.uuid4())
    scope_1 = "do_a_thing"
    scope_1_urn = f"urn:globus:auth:scope:{rs}:{scope_1}"

    none_sb = ScopeBuilder(rs, known_scopes=None)
    str_sb = ScopeBuilder(rs, known_scopes=scope_1)
    tuple_sb = ScopeBuilder(rs, known_scopes=("scope_1", scope_1))
    list_sb = ScopeBuilder(rs, known_scopes=[scope_1, ("scope_1", scope_1)])

    assert none_sb.scope_names == []
    assert scope_1 in str_sb.scope_names
    assert str_sb.do_a_thing == scope_1_urn
    assert "scope_1" in tuple_sb.scope_names
    assert tuple_sb.scope_1 == scope_1_urn
    assert scope_1 in list_sb.scope_names
    assert "scope_1" in list_sb.scope_names
    assert list_sb.scope_1 == scope_1_urn
    assert list_sb.do_a_thing == scope_1_urn


def test_scope_str_and_repr_simple():
    s = MutableScope("simple")
    assert str(s) == "simple"
    assert repr(s) == "MutableScope('simple')"


def test_scope_str_and_repr_optional():
    s = MutableScope("simple", optional=True)
    assert str(s) == "*simple"
    assert repr(s) == "MutableScope('simple', optional=True)"


def test_scope_str_and_repr_with_dependencies():
    s = MutableScope("top")
    s.add_dependency("foo")
    assert str(s) == "top[foo]"
    s.add_dependency("bar")
    assert str(s) == "top[foo bar]"
    assert (
        repr(s) == "MutableScope('top', "
        "dependencies=[MutableScope('foo'), MutableScope('bar')])"
    )


def test_add_dependency_warns_on_optional_but_still_has_good_str_and_repr():
    s = MutableScope("top")
    # this should warn, the use of `optional=...` rather than adding a Scope object
    # when optional dependencies are wanted is deprecated
    with pytest.warns(DeprecationWarning):
        s.add_dependency("foo", optional=True)

    # confirm the str representation and repr for good measure
    assert str(s) == "top[*foo]"
    assert (
        repr(s)
        == "MutableScope('top', dependencies=[MutableScope('foo', optional=True)])"
    )


def test_scopebuilder_make_mutable_produces_same_strings():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo", known_url_scopes="bar")
    assert str(sb.make_mutable("foo")) == sb.foo
    assert str(sb.make_mutable("bar")) == sb.bar


def test_scopebuilder_make_mutable_can_be_optional():
    sb = ScopeBuilder(str(uuid.UUID(int=0)), known_scopes="foo")
    assert str(sb.make_mutable("foo", optional=True)) == "*" + sb.foo


def test_flows_scopes_creation():
    assert FlowsScopes.resource_server == "flows.globus.org"
    assert (
        FlowsScopes.run
        == "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
    )


@pytest.mark.parametrize("scope_str", ("*foo", "foo[bar]", "foo[", "foo]", "foo bar"))
def test_scope_init_forbids_special_chars(scope_str):
    with pytest.raises(ValueError):
        MutableScope(scope_str)
