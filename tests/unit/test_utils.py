import uuid

import pytest

from globus_sdk import utils


def test_sha256string():
    test_string = "foo"
    expected_sha = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"

    assert utils.sha256_string(test_string) == expected_sha


@pytest.mark.parametrize(
    "platform_value, result",
    (
        # platform.node() can return '' when it doesn't know the hostname
        # turn this into None
        pytest.param("", None, id="empty-is-none"),
        # macOS adds '.local' to the user's chosen machine name
        pytest.param(
            "VeryCoolMacbook.local", "VeryCoolMacbook", id="remove-local-suffix"
        ),
        # the "boring" case is when we do no extra work
        pytest.param("linux-workstation", "linux-workstation", id="boring"),
    ),
)
def test_get_nice_hostname(platform_value, result, monkeypatch):
    monkeypatch.setattr("platform.node", lambda: platform_value)
    assert utils.get_nice_hostname() == result


@pytest.mark.parametrize(
    "a, b",
    [(a, b) for a in ["a", "a/"] for b in ["b", "/b"]]
    + [("a/b", c) for c in ["", None]],  # type: ignore
)
def test_slash_join(a, b):
    """
    slash_joins a's with and without trailing "/"
    to b's with and without leading "/"
    Confirms all have the same correct slash_join output
    """
    assert utils.slash_join(a, b) == "a/b"


def test_payload_wrapper_methods():
    # just make sure that PayloadWrapper acts like a dict...
    data = utils.PayloadWrapper()
    assert "foo" not in data
    with pytest.raises(KeyError):
        data["foo"]
    data["foo"] = 1
    assert "foo" in data
    assert data["foo"] == 1
    del data["foo"]
    assert "foo" not in data
    assert len(data) == 0
    assert list(data) == []
    data["foo"] = 1
    data["bar"] = 2
    assert len(data) == 2
    assert data.data == {"foo": 1, "bar": 2}
    data.update({"x": "hello", "y": "world"})
    assert data.data == {"foo": 1, "bar": 2, "x": "hello", "y": "world"}


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("foo", ["foo"]),
        ((1, 2, 3), ["1", "2", "3"]),
        (uuid.UUID(int=10), [f"{uuid.UUID(int=10)}"]),
        (["foo", uuid.UUID(int=5)], ["foo", f"{uuid.UUID(int=5)}"]),
    ),
)
def test_safe_strseq_iter(value, expected_result):
    assert list(utils.safe_strseq_iter(value)) == expected_result
