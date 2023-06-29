import json

import pytest

from globus_sdk.exc import ErrorSubdocument, GlobusAPIError
from globus_sdk.experimental.session_error import (
    GlobusSessionError,
    has_session_errors,
    is_session_error,
    to_session_error,
    to_session_errors,
)

# TODO: We should move this to a common location
from tests.unit.errors.conftest import _mk_response


def _error_for_json_dict(error_dict, status=403, method="POST", headers=None):
    combined_headers = {"Content-Type": "application/json"}
    if headers:
        combined_headers.update(headers)

    response = _mk_response(
        data=error_dict,
        status=status,
        method=method,
        headers=combined_headers,
        data_transform=json.dumps,
    )
    return GlobusAPIError(response.r)


@pytest.mark.parametrize(
    "error_dict, status",
    (
        (
            {
                "code": "ConsentRequired",
                "message": "Missing required foo_bar consent",
                "request_id": "WmMV97A1w",
                "required_scopes": [
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
                ],
                "resource": "/transfer",
            },
            403,
        ),
        (
            {
                "code": "ConsentRequired",
                "required_scope": (
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
                ),
                "description": "Missing required foo_bar consent",
            },
            401,
        ),
    ),
)
def test_create_session_error_from_consent_error(error_dict, status):
    """
    Test that various ConsentRequired error shapes can be detected and converted
    to a GlobusSessionError.
    """
    # Create various supplementary objects representing this error
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = _error_for_json_dict(error_dict, status=status)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_session_error(error)
        assert has_session_errors([error])

        # Check that this only produces one error
        assert len(to_session_errors([error])) == 1

        # Create a session error from a Transfer format error
        session_error = to_session_error(error)
        assert isinstance(session_error, GlobusSessionError)
        assert session_error.code == "ConsentRequired"
        assert session_error.authorization_parameters.session_required_scopes == [
            "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
        ]
        assert (
            session_error.authorization_parameters.session_message
            == "Missing required foo_bar consent"
        )


@pytest.mark.parametrize(
    "authorization_parameters",
    (
        {
            "session_message": (
                "To gain access you need to authenticate with your baz identity"
            ),
            "session_required_identities": ["urn:globus:auth:identity:baz"],
            "session_required_mfa": True,
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": ["foo", "baz"],
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "belongs to an authorized domain"
            ),
            "session_required_single_domain": ["foo.com", "baz.org"],
        },
    ),
)
def test_create_session_error_from_authorization_error(authorization_parameters):
    """
    Test that various AuthorizationRequired error shapes can be detected and converted
    to a GlobusSessionError.
    """
    # Create various supplementary objects representing this error
    error_dict = {"authorization_parameters": authorization_parameters}
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = _error_for_json_dict(error_dict)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_session_error(error)
        assert has_session_errors([error])

        # Check that this only produces one error
        assert len(to_session_errors([error])) == 1

        # Create a session error from a legacy authorization parameters format error
        session_error = to_session_error(error)
        assert isinstance(session_error, GlobusSessionError)

        # Check that the default error code is set
        assert session_error.code == "AuthorizationRequired"

        # Iterate over the expected attributes and check that they match
        for name, value in authorization_parameters.items():
            assert getattr(session_error.authorization_parameters, name) == value


@pytest.mark.parametrize(
    "authorization_parameters",
    (
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": ["foo", "baz"],
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "belongs to an authorized domain"
            ),
            "session_required_single_domain": ["foo.com", "baz.org"],
        },
    ),
)
def test_create_session_error_from_authorization_error_csv(authorization_parameters):
    """
    Test that AuthorizationRequired error shapes that provide lists as comma-delimited
    values can be detected and converted to a GlobusSessionError normalizing to
    lists of strings for those values.
    """
    # Create various supplementary objects representing this error
    error_dict = {"authorization_parameters": {}}
    for key, value in authorization_parameters.items():
        if key in ("session_required_policies", "session_required_single_domain"):
            # Convert the list to a comma-separated string for known variants
            error_dict["authorization_parameters"][key] = ",".join(value)
        else:
            error_dict["authorization_parameters"][key] = value

    error_subdoc = ErrorSubdocument(error_dict)
    api_error = _error_for_json_dict(error_dict)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_session_error(error)
        assert has_session_errors([error])

        # Check that this only produces one error
        assert len(to_session_errors([error])) == 1

        # Create a session error from a legacy authorization parameters format error
        session_error = to_session_error(error)
        assert isinstance(session_error, GlobusSessionError)

        # Check that the default error code is set
        assert session_error.code == "AuthorizationRequired"

        # Iterate over the expected attributes and check that they match
        for name, value in authorization_parameters.items():
            assert getattr(session_error.authorization_parameters, name) == value


def test_create_session_errors_from_multiple_errors():
    """
    Test that a GlobusAPIError with multiple subdocuments is converted to multiple
    GlobusSessionErrors, and additionally test that this is correct even when mingled
    with other accepted data types.
    """
    consent_errors = _error_for_json_dict(
        {
            "errors": [
                {
                    "code": "ConsentRequired",
                    "message": "Missing required foo_bar consent",
                    "authorization_parameters": {
                        "session_required_scopes": [
                            "urn:globus:auth:scope:transfer.api.globus.org:all[*bar]"
                        ],
                        "session_message": "Missing required foo_bar consent",
                    },
                },
                {
                    "code": "ConsentRequired",
                    "message": "Missing required foo_baz consent",
                    "authorization_parameters": {
                        "session_required_scopes": [
                            "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
                        ],
                        "session_message": "Missing required foo_baz consent",
                    },
                },
            ]
        }
    )

    authorization_error = _error_for_json_dict(
        {
            "authorization_parameters": {
                "session_message": (
                    "You need to authenticate with an identity that "
                    "matches the required policies"
                ),
                "session_required_policies": ["foo", "baz"],
            }
        }
    )

    not_an_error = _error_for_json_dict(
        {
            "code": "NotAnError",
            "message": "This is not an error",
        }
    )

    all_errors = [consent_errors, not_an_error, authorization_error]

    # Test boolean utility function
    assert has_session_errors(all_errors)

    # Create session errors from a all errors
    session_errors = to_session_errors(all_errors)
    assert isinstance(session_errors, list)
    assert len(session_errors) == 3

    # Check that errors properly converted
    for session_error in session_errors:
        assert isinstance(session_error, GlobusSessionError)

    # Check that the proper session errors were produced
    assert session_errors[0].code == "ConsentRequired"
    assert session_errors[0].authorization_parameters.session_required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*bar]"
    ]
    assert (
        session_errors[0].authorization_parameters.session_message
        == "Missing required foo_bar consent"
    )
    assert session_errors[1].code == "ConsentRequired"
    assert session_errors[1].authorization_parameters.session_required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
    ]
    assert (
        session_errors[1].authorization_parameters.session_message
        == "Missing required foo_baz consent"
    )
    assert session_errors[2].code == "AuthorizationRequired"
    assert session_errors[2].authorization_parameters.session_required_policies == [
        "foo",
        "baz",
    ]
    assert session_errors[2].authorization_parameters.session_message == (
        "You need to authenticate with an identity that matches the required policies"
    )


def test_create_session_error_from_legacy_authorization_error_with_code():
    """
    Test that legacy AuthorizationRequired error shapes that provide a `code` can be
    detected and converted to a GlobusSessionError while retaining the `code`.
    """
    # Create a legacy authorization parameters error with a code
    error_dict = {
        "code": "UnsatisfiedPolicy",
        "authorization_parameters": {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": "foo,baz",
        },
    }

    # Create various supplementary objects representing this error
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = _error_for_json_dict(error_dict)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_session_error(error)
        assert has_session_errors([error])

        # Check that this only produces one error
        assert len(to_session_errors([error])) == 1

        # Create a session error from a legacy authorization parameters format error
        session_error = to_session_error(error)
        assert isinstance(session_error, GlobusSessionError)

        # Check that the custom error code is set
        assert session_error.code == "UnsatisfiedPolicy"

        # Iterate over the expected attributes and check that they match
        assert session_error.authorization_parameters.session_required_policies == [
            "foo",
            "baz",
        ]


def test_backward_compatibility_consent_required_error():
    """
    Test that a consent required error with a comingled backward-compatible
    data schema is converted to a GlobusSessionError.
    """
    # Create an API error with a backward compatible data schema using
    # distinct values for duplicative fields to facilitate testing
    # (in practice these would be the same)
    error = _error_for_json_dict(
        {
            "code": "ConsentRequired",
            "message": "Missing required foo_bar consent",
            "request_id": "WmMV97A1w",
            "required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
            ],
            "resource": "/transfer",
            "authorization_parameters": {
                "session_message": "Missing baz consent",
                "session_required_scopes": [
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
                ],
                "session_required_policies": "foo,bar",
                "optional": "A non-canonical field",
            },
        },
        status=403,
    )

    # Test boolean utility functions
    assert is_session_error(error)
    assert has_session_errors([error])

    # Check that this only produces one error
    assert len(to_session_errors([error])) == 1

    # Create a session error
    session_error = to_session_error(error)
    assert isinstance(session_error, GlobusSessionError)
    assert session_error.code == "ConsentRequired"
    assert session_error.authorization_parameters.session_required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
    ]
    assert (
        session_error.authorization_parameters.session_message == "Missing baz consent"
    )

    # Test that only suppotred fields are present in the dict
    assert session_error.to_dict() == {
        "code": "ConsentRequired",
        "authorization_parameters": {
            "session_message": "Missing baz consent",
            "session_required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
            ],
            "session_required_policies": ["foo", "bar"],
        },
    }

    # Test that extra fields are present in the dict
    assert session_error.to_dict(include_extra=True) == {
        "code": "ConsentRequired",
        "message": "Missing required foo_bar consent",
        "request_id": "WmMV97A1w",
        "required_scopes": [
            "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
        ],
        "resource": "/transfer",
        "authorization_parameters": {
            "session_message": "Missing baz consent",
            "session_required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
            ],
            "session_required_policies": ["foo", "bar"],
            "optional": "A non-canonical field",
        },
    }
