import pytest

from globus_sdk import GCSAPIError
from tests.common import register_api_route_fixture_file


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
