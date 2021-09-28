import base64
import hashlib
import os

import pytest

from globus_sdk import GlobusSDKUsageError
from globus_sdk.services.auth.flow_managers.native_app import make_native_app_challenge


@pytest.mark.parametrize(
    "verifier",
    [
        "x" * 20,  # too short
        "x" * 200,  # too long
        ("x" * 40) + "/" + ("y" * 40),  # includes invalid characters
    ],
)
def test_invalid_native_app_challenge(verifier):
    with pytest.raises(GlobusSDKUsageError):
        make_native_app_challenge(verifier)


def test_simple_input_native_app_challenge():
    verifier = "x" * 80
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest())
        .rstrip(b"=")
        .decode("utf-8")
    )
    res_verifier, res_challenge = make_native_app_challenge(verifier)
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

    verifier, challenge = make_native_app_challenge()
    assert verifier == "abc123"
    assert challenge == "abc123"

    assert len(b64vals) == 2
    assert b64vals == [b"xyz", hashlib.sha256(b"abc123").digest()]
