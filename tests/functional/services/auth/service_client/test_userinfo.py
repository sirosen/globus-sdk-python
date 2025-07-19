import pytest

import globus_sdk
from globus_sdk.testing import load_response


# TODO: add data for the success case and test it
@pytest.mark.xfail
def test_userinfo():
    raise NotImplementedError


@pytest.mark.parametrize("casename", ("unauthorized", "forbidden"))
def test_userinfo_error_handling(service_client, casename):
    meta = load_response(service_client.userinfo, case=casename).metadata

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        service_client.userinfo()

    err = excinfo.value
    assert err.http_status == meta["http_status"]
    assert err.code == meta["code"]
    assert err.request_id == meta["error_id"]
