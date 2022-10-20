from globus_sdk import FlowsClient
from globus_sdk._testing import load_response


def test_delete_flow(flows_client: FlowsClient):
    metadata = load_response(flows_client.delete_flow).metadata

    resp = flows_client.delete_flow(metadata["flow_id"])
    assert resp.data["title"] == "Multi Step Transfer"
    assert resp.data["DELETED"] is True
