import pytest

import globus_sdk
from globus_sdk._testing import load_response


def test_update_index(client):
    meta = load_response(client.update_index).metadata

    res = client.update_index(meta["index_id"], display_name="foo")
    assert res.http_status == 200
    assert res["display_name"] == meta["display_name"]


def test_update_index_forbidden_error(client):
    meta = load_response(client.update_index, case="forbidden").metadata

    with pytest.raises(globus_sdk.SearchAPIError) as excinfo:
        client.update_index(meta["index_id"])

    err = excinfo.value

    assert err.http_status == 403
    assert err.code == "Forbidden.Generic"
