from globus_sdk.services.groups import client
from tests.common import register_api_route_fixture_file


def test_my_groups_simple(groups_client):
    register_api_route_fixture_file("groups", "/v2/groups/my_groups", "my_groups.json")

    res = groups_client.get_my_groups()
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, list)
    assert "duke" in [g["name"] for g in data]


def test_get_group(groups_client):
    register_api_route_fixture_file(
        "groups", "/v2/groups/d3974728-6458-11e4-b72d-123139141556", "group.json"
    )

    res = groups_client.get_group(group_id="d3974728-6458-11e4-b72d-123139141556")
    assert res.http_status == 200

    data = res.data
    assert "Claptrap" in data["name"]


def test_delete_group(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556",
        "group.json",
        method="DELETE",
    )

    res = groups_client.delete_group(group_id="d3974728-6458-11e4-b72d-123139141556")
    assert res.http_status == 200

    data = res.data
    assert "Claptrap" in data["name"]


def test_create_group(groups_manager):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups",
        "created_group.json",
        method="POST",
    )

    res = groups_manager.create_group(
        name="Claptrap's Rough Riders", description="No stairs allowed."
    )
    assert res.http_status == 200
    assert "Claptrap" in res.data["name"]
    assert "No stairs allowed." in res.data["description"]


def test_get_group_policies(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "get_group_policies.json",
    )
    resp = groups_client.get_group_policies("d3974728-6458-11e4-b72d-123139141556")
    assert resp.http_status == 200
    assert resp.data == {
        "is_high_assurance": False,
        "authentication_assurance_timeout": 28800,
        "group_visibility": "private",
        "group_members_visibility": "managers",
        "join_requests": False,
        "signup_fields": [],
    }


def test_set_group_policies(groups_manager):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "set_group_policies.json",
        method="PUT",
    )
    resp = groups_manager.set_group_policies(
        "d3974728-6458-11e4-b72d-123139141556",
        False,
        client.GroupVisibility.private,
        client.GroupMemberVisibility.managers,
        False,
        [client.RequiredSignupFields.address1],
        28800,
    )
    assert resp.http_status == 200
    assert "address1" in resp.data["signup_fields"]
