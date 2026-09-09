import base64
import hashlib
import os
from unittest import mock

import pytest

import globus_sdk
from globus_sdk import MISSING
from globus_sdk.scopes import TransferScopes
from globus_sdk.services.auth.flow_managers.authorization_code import (
    GlobusAuthorizationCodeFlowManager,
)
from globus_sdk.services.auth.flow_managers.native_app import _make_native_app_challenge


@pytest.mark.parametrize(
    "verifier",
    [
        "x" * 20,  # too short
        "x" * 200,  # too long
        ("x" * 40) + "/" + ("y" * 40),  # includes invalid characters
    ],
)
def test_invalid_native_app_challenge(verifier):
    with pytest.raises(globus_sdk.GlobusSDKUsageError):
        _make_native_app_challenge(verifier)


def test_simple_input_native_app_challenge():
    verifier = "x" * 80
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("utf-8")
    )
    res_verifier, res_challenge = _make_native_app_challenge(verifier)
    assert res_verifier == verifier
    assert res_challenge == challenge


def test_random_native_app_challenge(monkeypatch):
    b64vals = []

    def mock_urandom(n: int):
        return b"xyz"

    def mock_b64encode(b: bytes):
        b64vals.append(b)
        return b"abc123"

    monkeypatch.setattr(os, "urandom", mock_urandom)
    monkeypatch.setattr(base64, "urlsafe_b64encode", mock_b64encode)

    verifier, challenge = _make_native_app_challenge()
    assert verifier == "abc123"
    assert challenge == "abc123"

    assert len(b64vals) == 2
    assert b64vals == [b"xyz", hashlib.sha256(b"abc123").digest()]


def test_get_authorize_url_for_authorization_code():
    mock_client = mock.Mock()
    mock_client.client_id = "MOCK_CLIENT_ID"
    mock_client.base_url = "https://auth.globus.org/"
    flow_manager = GlobusAuthorizationCodeFlowManager(
        mock_client,
        redirect_uri="https://foo.example.org/authenticate",
        requested_scopes=TransferScopes.all,
    )

    value = ["apples", "bananas"]

    authorize_url = flow_manager.get_authorize_url()
    assert authorize_url.startswith("https://auth.globus.org")
    assert "session_required_identities=" not in authorize_url

    fruity_authorize_url = flow_manager.get_authorize_url(
        query_params={"session_required_identities": value}
    )
    assert "session_required_identities=apples%2Cbananas" in fruity_authorize_url


@pytest.mark.parametrize("parameter", ("base_query_params", "query_params"))
@pytest.mark.parametrize(
    "key",
    (
        "session_required_identities",
        "session_required_single_domain",
        "session_required_policies",
    ),
)
def test_get_authorize_url_formatting(parameter, key):
    """
    Verify 'session_required_*' values are comma-joined.

    Prioritization of *query_params* over *base_query_params* is also tested
    by confirming that the "wrong-value" in *base_query_params* is overridden
    when the *key* is set in *query_params*.
    """

    # Arrange
    parameters = {
        "base_url": "https://auth.globus.org/",
        "base_query_params": {
            "session_required_identities": "wrong-value",
            "session_required_single_domain": "wrong-value",
            "session_required_policies": "wrong-value",
        },
        "query_params": {},
    }
    parameters[parameter][key] = ["correct", "value"]

    # Act
    url = GlobusAuthorizationCodeFlowManager._get_authorize_url(**parameters)

    # Assert
    assert f"{key}=correct%2Cvalue" in url


@pytest.mark.parametrize("parameter", ("base_query_params", "query_params"))
@pytest.mark.parametrize(
    "key",
    (
        "session_required_identities",
        "session_required_single_domain",
        "session_required_policies",
    ),
)
@pytest.mark.parametrize("value", (MISSING, None, []))
def test_get_authorize_url_exclusions(key, parameter, value):
    """Verify false-y 'session_required_*' values not serialized."""

    # Arrange
    parameters = {
        "base_url": "https://auth.globus.org/",
        "base_query_params": {
            "session_required_identities": "wrong-value",
            "session_required_single_domain": "wrong-value",
            "session_required_policies": "wrong-value",
        },
        "query_params": {},
    }
    parameters[parameter][key] = value

    # Act
    url = GlobusAuthorizationCodeFlowManager._get_authorize_url(**parameters)

    # Assert
    assert f"{key}=" not in url
