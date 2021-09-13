import pytest

from globus_sdk.services.gcs import UnpackingGCSResponse
from tests.common import make_response


def test_unpacking_response_with_callback():
    def identify_desired_data(d):
        return "foo" in d

    base_resp = make_response(
        json_body={
            "data": [
                {"x": 1, "y": 2},
                {"x": 2, "y": 3, "foo": "bar"},
            ]
        }
    )

    resp = UnpackingGCSResponse(base_resp, identify_desired_data)
    assert resp["x"] == 2
    assert resp["y"] == 3
    assert resp["foo"] == "bar"


@pytest.mark.parametrize("datatype", ["foo#1.0.1", "foo#1", "foo#0.0.1", "foo#2.0.0.1"])
def test_unpacking_response_matches_datatype(datatype):
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": datatype}]})
    resp = UnpackingGCSResponse(base_resp, "foo")
    assert "x" in resp
    # using some other spec will not match
    resp_bar = UnpackingGCSResponse(base_resp, "bar")
    assert "x" not in resp_bar


def test_unpacking_response_invalid_spec():
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": "foo#1.0.0"}]})
    with pytest.raises(ValueError):
        UnpackingGCSResponse(base_resp, "foo 1.0")


def test_unpacking_response_invalid_datatype():
    # we'll never return a match if the DATA_TYPE doesn't appear to be valid
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": "foo"}]})
    resp = UnpackingGCSResponse(base_resp, "foo")
    assert "x" not in resp
