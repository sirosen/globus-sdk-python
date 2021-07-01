from tests.common import register_api_route_fixture_file


def test_my_groups_simple(groups_client):
    register_api_route_fixture_file("groups", "/v2/groups/my_groups", "my_groups.json")

    res = groups_client.get("/groups/my_groups")
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, list)
    assert "duke" in [g["name"] for g in data]
