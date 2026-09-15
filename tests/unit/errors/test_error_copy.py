"""
Several errors define `__reduce__` to ensure that they are pickleable.

These tests ensure that we can copy without errors and that the results compare equal
under some definition of "equal" (which may be specific to the error type).
"""

import copy

from globus_sdk.exc import NetworkError
from globus_sdk.scopes.consents import ConsentParseError, ConsentTreeConstructionError
from globus_sdk.token_storage.validating_token_storage import (
    ExpiredTokenError,
    IdentityMismatchError,
    MissingTokenError,
    UnmetScopeRequirementsError,
)


def test_copy_of_network_error():
    err = NetworkError("bad cxn", Exception("kaboom"))
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert str(err_copy.underlying_exception) == "kaboom"


def test_copy_of_identity_mismatch_error():
    err = IdentityMismatchError("they didn't match", "a", "b")
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.stored_id,
        err.new_id,
    ) == (
        err_copy.message,
        err_copy.stored_id,
        err_copy.new_id,
    )


def test_copy_of_missing_token_error():
    err = MissingTokenError("it gone", "my_rs")
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.resource_server,
    ) == (
        err_copy.message,
        err_copy.resource_server,
    )


def test_copy_of_expired_token_error():
    err = ExpiredTokenError(101)
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.expiration,
    ) == (
        err_copy.message,
        err_copy.expiration,
    )


def test_copy_of_scope_requirements_error():
    err = UnmetScopeRequirementsError("needed a token for scope", {"my_rs": []})
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.scope_requirements,
    ) == (
        err_copy.message,
        err_copy.scope_requirements,
    )


def test_copy_of_consent_parse_error():
    err = ConsentParseError("it didn't parse", {})
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.raw_consent,
    ) == (
        err_copy.message,
        err_copy.raw_consent,
    )


def test_copy_of_consent_tree_construction_error():
    err = ConsentTreeConstructionError("empty", [])
    err_copy = copy.copy(err)
    assert id(err) != id(err_copy)
    assert (
        err.message,
        err.consents,
    ) == (
        err_copy.message,
        err_copy.consents,
    )
