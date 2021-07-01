from globus_sdk.services.groups import client
from tests.common import register_api_route_fixture_file


def test_approve_pending(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556",
        "approve_pending.json",
        method="POST",
    )

    res = groups_client.approve_pending(
        "d3974728-6458-11e4-b72d-123139141556", "ae332d86-d274-11e5-b885-b31714a110e9"
    )
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert "approve" in data
    assert data["approve"][0]["status"] == "active"


def test_add_member(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556",
        "add_member.json",
        method="POST",
    )

    res = groups_client.add_member(
        "d3974728-6458-11e4-b72d-123139141556",
        "ae332d86-d274-11e5-b885-b31714a110e9",
        client.Role.admin,
    )
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert "add" in data
    assert data["add"][0]["status"] == "active"
    assert data["add"][0]["role"] == "admin"


def test_batch_action_payload():
    batch_action = (
        client.BatchMembershipActions()
        .accept_invites(["ae332d86-d274-11e5-b885-b31714a110e9"])
        .add_members(
            [
                "788e8a5e-da7f-11eb-9782-97fc8494b14e",
                "79c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ],
            client.Role.manager,
        )
        .invite_members(
            [
                "888e8a5e-da7f-11eb-9782-97fc8494b14e",
                "89c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ]
        )
        .join(
            [
                "888e8a5e-da7f-11eb-9782-97fc8494b14e",
                "89c411f0-da7f-11eb-a0e4-a3451dad6f05",
            ]
        )
    )
    payload = batch_action.to_dict()

    assert "add" in payload
    assert len(payload["add"]) == 2
    assert all(member["role"] == "manager" for member in payload["add"])

    assert "accept" in payload
    assert len(payload["accept"]) == 1

    assert "invite" in payload
    assert len(payload["invite"]) == 2

    assert "join" in payload
    assert len(payload["invite"]) == 2
