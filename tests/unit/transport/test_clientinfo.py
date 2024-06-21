import pytest

from globus_sdk import __version__
from globus_sdk.transport._clientinfo import DefaultGlobusClientInfo, GlobusClientInfo


def parse_clientinfo(header):
    """
    Sample parser.

    Including this in the testsuite not only validates the mechanical implementation of
    X-Globus-Client-Info, but also acts as a safety check that we've thought through the
    ability of consumers to parse this data.
    """
    mappings = {}
    for segment in header.split(";"):
        segment_dict = {}

        segment = segment.strip()
        elements = segment.split(",")

        for element in elements:
            if "=" not in element:
                raise ValueError(
                    f"Bad X-Globus-Client-Info element: '{element}' in '{header}'"
                )
            key, _, value = element.partition("=")
            if "=" in value:
                raise ValueError(
                    f"Bad X-Globus-Client-Info element: '{element}' in '{header}'"
                )
            if key in segment_dict:
                raise ValueError(
                    f"Bad X-Globus-Client-Info element: '{element}' in '{header}'"
                )
            segment_dict[key] = value
        if "product" not in segment_dict:
            raise ValueError(
                "Bad X-GlobusClientInfo segment missing product: "
                f"'{segment}' in '{header}'"
            )
        product = segment_dict["product"]
        if product in mappings:
            raise ValueError(
                "Bad X-GlobusClientInfo header repeats product: "
                f"'{product}' in '{header}'"
            )
        mappings[product] = segment_dict
    return mappings


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


def test_clientinfo_parses_as_expected():
    default = DefaultGlobusClientInfo()
    default.add("alpha=b01,product=my-cool-tool")
    header_str = default.format()

    parsed = parse_clientinfo(header_str)
    assert parsed == {
        "python-sdk": {
            "product": "python-sdk",
            "version": __version__,
        },
        "my-cool-tool": {
            "product": "my-cool-tool",
            "alpha": "b01",
        },
    }
