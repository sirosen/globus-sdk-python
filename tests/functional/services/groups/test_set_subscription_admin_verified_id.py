from tests.common import register_api_route_fixture_file


def test_set_subscription_admin_verified_id(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/subscription_admin_verified",
        "set_subscription_admin_verified_id.json",
        method="PUT",
    )

    res = groups_client.set_subscription_admin_verified_id(
        group_id="d3974728-6458-11e4-b72d-123139141556",
        subscription_id="43db2f9f-601b-4c36-bbaa-26a97555935c",
    )
    assert res.http_status == 200
    assert res.data["group_id"] == "d3974728-6458-11e4-b72d-123139141556"
    assert (
        res.data["subscription_admin_verified_id"]
        == "43db2f9f-601b-4c36-bbaa-26a97555935c"
    )
