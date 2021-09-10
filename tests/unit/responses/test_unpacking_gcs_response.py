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


@pytest.mark.parametrize(
    "badspec",
    [
        "foo",
        "foo>1.0.0.0",
        "foo<1.0.0.0",
        "foo==1.0.0.0",
        "foo>1,>2",
        "foo<1,>2",
        "foo=1",
        "foo>2,<1",
        "foo>=1,<=1",
    ],
)
def test_unpacking_response_rejects_invalid_spec(badspec):
    base_resp = make_response(json_body={"data": [{"x": 1, "y": 2}]})

    with pytest.raises(ValueError):
        UnpackingGCSResponse(base_resp, badspec)


@pytest.mark.parametrize(
    "spec, datatype",
    [
        ["foo>=1,<2", "foo#1.2.1"],
        ["foo>1", "foo#1.0.1"],
        ["foo>=1", "foo#1.0.1"],
        ["foo>=1", "foo#1.0.0"],
        ["foo==1", "foo#1.0.0"],
        ["foo<=1", "foo#1.0.0"],
        ["foo<=1", "foo#0.0.1"],
        ["foo<1", "foo#0.0.1"],
    ],
)
def test_unpacking_response_matches_datatype_version(spec, datatype):
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": datatype}]})
    resp = UnpackingGCSResponse(base_resp, spec)
    assert "x" in resp


@pytest.mark.parametrize(
    "spec, datatype",
    [
        ["foo>=1,<2", "foo#2.2.1"],
        ["foo>=1,<2", "foo#0.2.1"],
        ["foo>1", "foo#1.0.0"],
        ["foo>1", "foo#0.0.1"],
        ["foo==1", "foo#1.1.0"],
        ["foo<2", "foo#2.0.0"],
        ["foo<1", "foo#1.0.1"],
    ],
)
def test_unpacking_response_does_not_match_datatype_version(spec, datatype):
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": datatype}]})
    resp = UnpackingGCSResponse(base_resp, spec)
    assert "x" not in resp


@pytest.mark.parametrize(
    "datatype",
    ["foo#1.0.1.0", "foo", "foo#a.b.c"],
)
def test_unpacking_response_does_not_match_bad_datatype_version(datatype):
    base_resp = make_response(json_body={"data": [{"x": 1, "DATA_TYPE": datatype}]})
    resp = UnpackingGCSResponse(base_resp, "foo>0")
    assert "x" not in resp
