import uuid

import pytest

from globus_sdk.testing import get_last_request, load_response
from tests.common import fast_json


@pytest.mark.parametrize("use_uuid", [False, True])
def test_respond_to_web_input(flows_client, use_uuid):
    meta = load_response(flows_client.respond_to_web_input).metadata

    web_input_id_str = meta["web_input_id"]
    web_input_id = uuid.UUID(web_input_id_str) if use_uuid else web_input_id_str

    res = flows_client.respond_to_web_input(web_input_id, value=meta["option_id"])

    assert res.http_status == 200
    assert res["status"] == "ok"

    req = get_last_request()
    assert f"/web_inputs/{web_input_id_str}/respond" in req.url
    sent_payload = fast_json.loads(req.body)
    assert sent_payload == {"response": {"value": meta["option_id"]}}
