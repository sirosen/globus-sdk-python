"""
Several errors define `__str__` to ensure that args are formatted
(or dropped) as desired. These tests ensure that we get the right strings back.
"""

from globus_sdk.exc import NetworkError
from globus_sdk.scopes.consents import ConsentParseError, ConsentTreeConstructionError
from globus_sdk.token_storage.validating_token_storage import (
    ExpiredTokenError,
    IdentityMismatchError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)


def test_str_of_network_error():
    err = NetworkError("bad cxn", Exception("kaboom"))
    assert str(err) == "bad cxn"


def test_str_of_identity_mismatch_error():
    err = IdentityMismatchError("they didn't match", "a", "b")
    assert str(err) == "they didn't match"


def test_str_of_missing_token_error():
    err = MissingTokenError("it gone", "my_rs")
    assert str(err) == "it gone"


def test_str_of_expired_token_error():
    err = ExpiredTokenError(101)
    assert str(err).startswith("Token expired at ")


def test_str_of_scope_requirements_error():
    err = UnmetScopeRequirementsError("needed a token for scope", {"my_rs": []})
    assert str(err) == "needed a token for scope"


def test_str_of_consent_parse_error():
    err = ConsentParseError("it didn't parse", {})
    assert str(err) == "it didn't parse"


def test_str_of_consent_tree_construction_error():
    err = ConsentTreeConstructionError("empty", [])
    assert str(err) == "empty"
