from globus_sdk import MISSING
from globus_sdk.transport.representation_providers import RequestsRepresentationProvider


def test_deeply_nested_body():
    """Verify that `RecursionError` doesn't manifest with a deeply-nested POST body."""

    deepest = {
        "value": MISSING,
        "list": [MISSING],
        "dict": {"missing": MISSING},
    }

    deep = deepest
    for _ in range(1_000):
        deep = {
            "deep": [deep],
            "missing": MISSING,
        }
        pass

    provider = RequestsRepresentationProvider()
    result = provider._prepare_data(deep)

    # * The original `deepest` variable must not have been modified.
    assert "value" in deepest
    assert deepest["list"] == [MISSING]
    assert deepest["dict"] == {"missing": MISSING}

    # * "missing" must not appear in the result value.
    assert "missing" not in result
    assert "missing" not in result["deep"][0]["deep"][0]["deep"][0]
