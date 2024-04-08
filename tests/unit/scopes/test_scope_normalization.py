import pytest

from globus_sdk.scopes import MutableScope, Scope, scopes_to_str


def test_scopes_to_str_roundtrip_simple_str():
    assert scopes_to_str("scope1") == "scope1"


def test_scopes_to_str_stringifies_single_scope():
    assert scopes_to_str(Scope("scope1")) == "scope1"


@pytest.mark.parametrize(
    "scope_collection",
    (
        ("scope1",),
        ["scope1"],
        {"scope1"},
        (s for s in ["scope1"]),
    ),
)
def test_scopes_to_str_roundtrip_simple_str_in_collection(scope_collection):
    assert scopes_to_str(scope_collection) == "scope1"


@pytest.mark.parametrize(
    "scope_collection, expect_str",
    (
        (("scope1", Scope("scope2")), "scope1 scope2"),
        (("scope1", MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2")), "scope1 scope2"),
        ((Scope("scope1"), MutableScope("scope2"), "scope3"), "scope1 scope2 scope3"),
    ),
)
def test_scopes_to_str_handles_mixed_data(scope_collection, expect_str):
    assert scopes_to_str(scope_collection) == expect_str
