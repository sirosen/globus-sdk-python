import urllib.parse

from globus_sdk.response import ArrayResponse
from globus_sdk.testing import get_last_request, load_response


def test_get_my_groups(groups_client):
    meta = load_response(groups_client.get_my_groups).metadata

    res = groups_client.get_my_groups(statuses="active")
    assert res.http_status == 200

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    assert parsed_qs["statuses"] == ["active"]

    assert isinstance(res, ArrayResponse)
    assert isinstance(res.data, list)
    assert set(meta["group_names"]) == {g["name"] for g in res}
