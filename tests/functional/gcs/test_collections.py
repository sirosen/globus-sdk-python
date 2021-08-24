import pytest

from globus_sdk import GCSAPIError
from tests.common import get_last_request, register_api_route_fixture_file


def test_get_collection_list(client):
    register_api_route_fixture_file("gcs", "/collections", "collection_list.json")
    res = client.get_collection_list()

    assert len(list(res)) == 2
    # sanity check some fields
    assert res["DATA_TYPE"] == "result#1.0.0"
    for item in res:
        assert item["DATA_TYPE"] == "collection#1.0.0"
        assert "id" in item
        assert item["id"] in ("{collection_id_1}", "{collection_id_2}")
        assert "display_name" in item


def test_get_collection_list_include_param(client):
    register_api_route_fixture_file("gcs", "/collections", "collection_list.json")

    client.get_collection_list()
    req = get_last_request()
    assert "include" not in req.params

    client.get_collection_list(include="foo")
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo"

    client.get_collection_list(include="foo,bar")
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo,bar"

    client.get_collection_list(include=("foo", "bar"))
    req = get_last_request()
    assert "include" in req.params
    assert req.params["include"] == "foo,bar"


def test_error_parsing_forbidden(client):
    register_api_route_fixture_file(
        "gcs", "/collections", "forbidden_error_data.json", status=403
    )
    with pytest.raises(GCSAPIError) as excinfo:
        client.get_collection_list()

    err = excinfo.value
    assert err.detail is None
    assert err.detail_data_type is None
    assert err.message.startswith("Could not list collections")
    assert err.code == "permission_denied"


def test_get_collection(client):
    # test on "correct" collection data, but also on a single dict response when a
    # singleton array is expected
    # in both cases, the endpoint data should be present
    # but in the "unexpectedly flat" case, the detail will be absent (because there is
    # no such field) and the expected shape method will return False

    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID_1", "get_collection.json"
    )
    register_api_route_fixture_file(
        "gcs", "/collections/COLLECTION_ID_2", "get_collection_unexpectedly_flat.json"
    )

    res = client.get_collection("COLLECTION_ID_1")
    assert res.data_has_expected_shape()
    assert res.original_data["detail"] == "success"
    assert res["display_name"] == "Happy Fun Collection Name"

    res = client.get_collection("COLLECTION_ID_2")
    assert not res.data_has_expected_shape()
    assert "detail" not in res.original_data
    assert res["display_name"] == "Happy Fun Collection Name"
