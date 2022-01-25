import json
import urllib.parse
import uuid

import pytest

import globus_sdk
from tests.common import get_last_request, register_api_route_fixture_file


@pytest.fixture
def search_client(no_retry_transport):
    class CustomSearchClient(globus_sdk.SearchClient):
        transport_class = no_retry_transport

    return CustomSearchClient()


def test_search_query_simple(search_client):
    index_id = str(uuid.uuid1())
    register_api_route_fixture_file(
        "search", f"/v1/index/{index_id}/search", "query_result_foo.json"
    )

    res = search_client.search(index_id, q="foo")
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs == {
        "q": ["foo"],
        "advanced": ["False"],
        "limit": ["10"],
        "offset": ["0"],
    }


@pytest.mark.parametrize(
    "query_doc",
    [
        {"q": "foo"},
        {"q": "foo", "limit": 10},
        globus_sdk.SearchQuery("foo"),
    ],
)
def test_search_post_query_simple(search_client, query_doc):
    index_id = str(uuid.uuid1())
    register_api_route_fixture_file(
        "search", f"/v1/index/{index_id}/search", "query_result_foo.json", method="POST"
    )

    res = search_client.post_search(index_id, query_doc)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body == dict(query_doc)


@pytest.mark.parametrize(
    "query_doc",
    [
        {"q": "foo", "limit": 10, "offset": 0},
        globus_sdk.SearchQuery("foo", limit=10, offset=0),
    ],
)
def test_search_post_query_arg_overrides(search_client, query_doc):
    index_id = str(uuid.uuid1())
    register_api_route_fixture_file(
        "search", f"/v1/index/{index_id}/search", "query_result_foo.json", method="POST"
    )

    res = search_client.post_search(index_id, query_doc, limit=100, offset=150)
    assert res.http_status == 200

    data = res.data
    assert isinstance(data, dict)
    assert data["gmeta"][0]["entries"][0]["content"]["foo"] == "bar"

    req = get_last_request()
    assert req.body is not None
    req_body = json.loads(req.body)
    assert req_body != dict(query_doc)
    assert req_body["q"] == query_doc["q"]
    assert req_body["limit"] == 100
    assert req_body["offset"] == 150
    # important! these should be unchanged (no side-effects)
    assert query_doc["limit"] == 10
    assert query_doc["offset"] == 0
