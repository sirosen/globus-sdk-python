import globus_sdk
from globus_sdk._testing import load_response


def test_get_endpoints(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_endpoints).metadata

    res = compute_client_v2.get_endpoints()

    assert res.http_status == 200
    assert res.data[0]["uuid"] == meta["endpoint_id"]
    assert res.data[1]["uuid"] == meta["endpoint_id_2"]


def test_get_endpoints_any(compute_client_v2: globus_sdk.ComputeClientV2):
    meta = load_response(compute_client_v2.get_endpoints, case="any").metadata
    res = compute_client_v2.get_endpoints(role="any")

    assert res.http_status == 200
    assert res.data[0]["uuid"] == meta["endpoint_id"]
    assert res.data[1]["uuid"] == meta["endpoint_id_2"]
    assert res.data[2]["uuid"] == meta["endpoint_id_3"]
    assert res.data[1]["owner"] != res.data[2]["owner"]
