import httpretty
import pytest

import globus_sdk
from tests.common import register_api_route

IDENTITIES_MULTIPLE_RESPONSE = """\
{
  "identities": [
    {
      "email": null,
      "id": "46bd0f56-e24f-11e5-a510-131bef46955c",
      "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
      "name": null,
      "organization": null,
      "status": "unused",
      "username": "globus@globus.org"
    },
    {
      "email": "sirosen@globus.org",
      "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
      "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
      "name": "Stephen Rosen",
      "organization": "Globus Team",
      "status": "used",
      "username": "sirosen@globus.org"
    }
  ]
}"""

IDENTITIES_SINGLE_RESPONSE = """\
{
  "identities": [
    {
      "email": "sirosen@globus.org",
      "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
      "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
      "name": "Stephen Rosen",
      "organization": "Globus Team",
      "status": "used",
      "username": "sirosen@globus.org"
    }
  ]
}"""


@pytest.fixture
def client():
    return globus_sdk.AuthClient()


def test_identity_map(client):
    register_api_route("auth", "/v2/api/identities", body=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client, ["sirosen@globus.org"])
    assert idmap["sirosen@globus.org"]["organization"] == "Globus Team"

    # lookup by ID also works
    assert (
        idmap["ae341a98-d274-11e5-b888-dbae3a8ba545"]["organization"] == "Globus Team"
    )

    # the last (only) API call was the one by username
    last_req = httpretty.last_request()
    assert "ids" not in last_req.querystring
    assert last_req.querystring["usernames"] == ["sirosen@globus.org"]
    assert last_req.querystring["provision"] == ["false"]


def test_identity_map_initialization_no_values(client):
    idmap = globus_sdk.IdentityMap(client)
    assert idmap.unresolved_ids == set()
    assert idmap.unresolved_usernames == set()


def test_identity_map_initialization_mixed_and_duplicate_values(client):
    # splits things up and deduplicates values into sets
    idmap = globus_sdk.IdentityMap(
        client,
        [
            "sirosen@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "globus@globus.org",
            "sirosen@globus.org",
            "globus@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "sirosen@globus.org",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
        ],
    )
    assert idmap.unresolved_ids == set(["ae341a98-d274-11e5-b888-dbae3a8ba545"])
    assert idmap.unresolved_usernames == set(
        ["sirosen@globus.org", "globus@globus.org"]
    )


def test_identity_map_initialization_batch_size(client):
    idmap = globus_sdk.IdentityMap(client, id_batch_size=10)
    assert idmap.unresolved_ids == set()
    assert idmap.unresolved_usernames == set()
    assert idmap.id_batch_size == 10


def test_identity_map_add(client):
    idmap = globus_sdk.IdentityMap(client)
    assert idmap.add("sirosen@globus.org") is True
    assert idmap.add("sirosen@globus.org") is False
    assert idmap.add("46bd0f56-e24f-11e5-a510-131bef46955c") is True
    assert idmap.add("46bd0f56-e24f-11e5-a510-131bef46955c") is False


def test_identity_map_add_after_lookup(client):
    register_api_route("auth", "/v2/api/identities", body=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    x = idmap["sirosen@globus.org"]["id"]
    # this is the key: adding it will indicate that we've already seen this ID, perhaps
    # "unintuitively", and that's part of the value of `add()` returning a boolean value
    assert idmap.add(x) is False
    assert idmap[x] == idmap["sirosen@globus.org"]


def test_identity_map_multiple(client):
    register_api_route(
        "auth", ("/v2/api/identities"), body=IDENTITIES_MULTIPLE_RESPONSE
    )
    idmap = globus_sdk.IdentityMap(client, ["sirosen@globus.org", "globus@globus.org"])
    assert idmap["sirosen@globus.org"]["organization"] == "Globus Team"
    assert idmap["globus@globus.org"]["organization"] is None

    last_req = httpretty.last_request()
    # order doesn't matter, but it should be just these two
    # if IdentityMap doesn't deduplicate correctly, it could send
    # `sirosen@globus.org,globus@globus.org,sirosen@globus.org` on the first lookup
    assert last_req.querystring["usernames"] in [
        ["sirosen@globus.org,globus@globus.org"],
        ["globus@globus.org,sirosen@globus.org"],
    ]
    assert last_req.querystring["provision"] == ["false"]


def test_identity_map_keyerror(client):
    register_api_route("auth", "/v2/api/identities", body=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    # a name which doesn't come back, indicating that it was not found, will KeyError
    with pytest.raises(KeyError):
        idmap["sirosen2@globus.org"]

    last_req = httpretty.last_request()
    assert last_req.querystring["usernames"] == ["sirosen2@globus.org"]
    assert last_req.querystring["provision"] == ["false"]


def test_identity_map_get_with_default(client):
    register_api_route("auth", "/v2/api/identities", body=IDENTITIES_SINGLE_RESPONSE)
    magic = object()  # sentinel value
    idmap = globus_sdk.IdentityMap(client)
    # a name which doesn't come back, if looked up with `get()` should return the
    # default
    assert idmap.get("sirosen2@globus.org", magic) is magic


def test_identity_map_del(client):
    register_api_route("auth", "/v2/api/identities", body=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    identity_id = idmap["sirosen@globus.org"]["id"]
    del idmap[identity_id]
    assert idmap.get("sirosen@globus.org")["id"] == identity_id
    # we've only made one request so far
    assert len(httpretty.httpretty.latest_requests) == 1
    # but a lookup by ID after a del is going to trigger another request because we've
    # invalidated the cached ID data and are asking the IDMap to look it up again
    assert idmap.get(identity_id)["username"] == "sirosen@globus.org"
    assert len(httpretty.httpretty.latest_requests) == 2
