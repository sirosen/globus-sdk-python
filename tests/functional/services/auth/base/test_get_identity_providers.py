import pytest

import globus_sdk
from globus_sdk._testing import get_last_request, load_response


def test_get_identity_providers_by_domains(client):
    meta = load_response(client.get_identity_providers).metadata
    res = client.get_identity_providers(domains=meta["domains"])

    assert [x["id"] for x in res] == meta["ids"]

    lastreq = get_last_request()
    assert lastreq.params == {"domains": ",".join(meta["domains"])}


def test_get_identity_providers_by_ids(client):
    meta = load_response(client.get_identity_providers).metadata
    res = client.get_identity_providers(ids=meta["ids"])

    assert [x["id"] for x in res] == meta["ids"]
    assert [x for y in res for x in y["domains"]] == meta["domains"]

    lastreq = get_last_request()
    assert lastreq.params == {"ids": ",".join(meta["ids"])}


def test_get_identity_providers_mutex_args(client):
    with pytest.raises(globus_sdk.GlobusSDKUsageError, match="mutually exclusive"):
        client.get_identity_providers(ids="foo", domains="bar")
