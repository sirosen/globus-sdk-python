import uuid

import pytest

from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize("use_uuid", [False, True])
def test_get_web_input(flows_client, use_uuid):
    loaded_response = load_response(flows_client.get_web_input)
    json, meta = loaded_response.json, loaded_response.metadata

    web_input_id_str = meta["web_input_id"]
    web_input_id = uuid.UUID(web_input_id_str) if use_uuid else web_input_id_str

    res = flows_client.get_web_input(web_input_id)

    assert res.http_status == 200
    assert res["id"] == web_input_id_str
    assert res["status"] == json["status"]
    assert res["input_type"] == json["input_type"]
    assert res["flow"]["id"] == meta["flow_id"]
    assert res["run"]["id"] == meta["run_id"]

    req = get_last_request()
    assert req.body is None
    assert f"/web_inputs/{web_input_id_str}" in req.url
