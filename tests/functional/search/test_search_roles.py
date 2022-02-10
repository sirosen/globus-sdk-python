import json

import pytest

import globus_sdk
from tests.common import get_last_request, register_api_route_fixture_file

ROLE_ID = "MDQ1MzAy"
INDEX_ID = "60d1160b-f016-40b0-8545-99619865873d"


@pytest.fixture
def search_client(no_retry_transport):
    class CustomSearchClient(globus_sdk.SearchClient):
        transport_class = no_retry_transport

    return CustomSearchClient()


def test_search_role_create(search_client):
    register_api_route_fixture_file(
        "search", f"/v1/index/{INDEX_ID}/role", "role_create.json", method="POST"
    )

    urn = "urn:globus:auth:identity:46bd0f56-e24f-11e5-a510-131bef46955c"
    data = {"role_name": "writer", "principal": urn}

    res = search_client.create_role(INDEX_ID, data)
    assert res.http_status == 200
    assert res["index_id"] == INDEX_ID
    assert res["role_name"] == "writer"

    last_req = get_last_request()
    sent = json.loads(last_req.body)
    assert sent == data


def test_search_role_delete(search_client):
    register_api_route_fixture_file(
        "search",
        f"/v1/index/{INDEX_ID}/role/{ROLE_ID}",
        "role_delete.json",
        method="DELETE",
    )

    res = search_client.delete_role(INDEX_ID, ROLE_ID)
    assert res.http_status == 200
    assert res["success"] is True
    assert res["deleted"]["index_id"] == INDEX_ID
    assert res["deleted"]["id"] == ROLE_ID


def test_search_role_list(search_client):
    register_api_route_fixture_file(
        "search", f"/v1/index/{INDEX_ID}/role_list", "role_list.json"
    )

    res = search_client.get_role_list(INDEX_ID)
    assert res.http_status == 200
    role_list = res["role_list"]
    assert isinstance(role_list, list)
    assert len(role_list) == 2
