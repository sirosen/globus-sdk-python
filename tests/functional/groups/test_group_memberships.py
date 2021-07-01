from tests.common import register_api_route_fixture_file


def test_approve_pending(groups_client):
    register_api_route_fixture_file("groups", "/v2/groups/d3974728-6458-11e4-b72d-123139141556", "join_approve.json", method="POST")

    res = groups_client.approve_pending("d3974728-6458-11e4-b72d-123139141556", "ae332d86-d274-11e5-b885-b31714a110e9")
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert "approve" in data
    assert data["approve"][0]["status"] == "active"


