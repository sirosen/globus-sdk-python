# coding=utf-8
from globus_sdk import utils


def test_safe_b64encode_non_ascii():
    test_string = "ⓤⓢⓔⓡⓝⓐⓜⓔ"
    expected_b64 = "4pOk4pOi4pOU4pOh4pOd4pOQ4pOc4pOU"

    assert utils.safe_b64encode(test_string) == expected_b64


def test_safe_b64encode_ascii():
    test_string = "username"
    expected_b64 = "dXNlcm5hbWU="

    assert utils.safe_b64encode(test_string) == expected_b64


def test_sha256string():
    test_string = "foo"
    expected_sha = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f" "98a5e886266e7ae"

    assert utils.sha256_string(test_string) == expected_sha
