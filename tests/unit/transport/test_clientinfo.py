import pytest

from globus_sdk.transport._clientinfo import DefaultGlobusClientInfo, GlobusClientInfo


def test_clientinfo_bool_after_init():
    # base clientinfo starts empty and should bool false
    base = GlobusClientInfo()
    assert bool(base) is False
    # default clientinfo starts with the SDK version and should bool true
    default = DefaultGlobusClientInfo()
    assert bool(default) is True


@pytest.mark.parametrize(
    "value, expect_str",
    (
        ("x=y", "x=y"),
        ("x=y,omicron=iota", "x=y,omicron=iota"),
        ({"x": "y"}, "x=y"),
        ({"x": "y", "alpha": "b01"}, "x=y,alpha=b01"),
    ),
)
def test_format_of_simple_item(value, expect_str):
    info = GlobusClientInfo()
    info.add(value)
    assert info.format() == expect_str


@pytest.mark.parametrize(
    "values, expect_str",
    (
        (("x=y",), "x=y"),
        (("x=y", "alpha=b01,omicron=iota"), "x=y;alpha=b01,omicron=iota"),
    ),
)
def test_format_of_multiple_items(values, expect_str):
    info = GlobusClientInfo()
    for value in values:
        info.add(value)
    assert info.format() == expect_str
