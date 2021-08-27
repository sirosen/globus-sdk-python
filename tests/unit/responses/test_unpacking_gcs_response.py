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
