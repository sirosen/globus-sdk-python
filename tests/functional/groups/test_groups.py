import json

from globus_sdk import (
    GroupMemberVisibility,
    GroupPolicies,
    GroupRequiredSignupFields,
    GroupVisibility,
)
from tests.common import get_last_request, register_api_route_fixture_file


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
        GroupVisibility.private,
        GroupMemberVisibility.managers,
        False,
        [GroupRequiredSignupFields.address1],
        28800,
    )
    assert resp.http_status == 200
    assert "address1" in resp.data["signup_fields"]
    # ensure enums were stringified correctly
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == "private"
    assert req_body["group_members_visibility"] == "managers"
    assert req_body["signup_fields"] == ["address1"]


def test_set_group_policies_explicit_payload(groups_client):
    register_api_route_fixture_file(
        "groups",
        "/v2/groups/d3974728-6458-11e4-b72d-123139141556/policies",
        "set_group_policies.json",
        method="PUT",
    )
    # same payload as the above test, but formulated without GroupsManager
    payload = GroupPolicies(
        False,
        GroupVisibility.private,
        GroupMemberVisibility.managers,
        False,
        [GroupRequiredSignupFields.address1],
        28800,
    )
    # set a string in the payload directly
    # this will pass through GroupPolicies.__setitem__
    payload["group_visibility"] = "authenticated"
    # now send it... (but ignore the response)
    groups_client.set_group_policies("d3974728-6458-11e4-b72d-123139141556", payload)
    # ensure enums were stringified correctly, but also that the raw string came through
    req = get_last_request()
    req_body = json.loads(req.body)
    assert req_body["group_visibility"] == "authenticated"
    assert req_body["group_members_visibility"] == "managers"
    assert req_body["signup_fields"] == ["address1"]
