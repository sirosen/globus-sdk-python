import pytest
import responses

import globus_sdk
from tests.common import get_last_request, register_api_route

IDENTITIES_MULTIPLE_RESPONSE = {
    "identities": [
        {
            "email": None,
            "id": "46bd0f56-e24f-11e5-a510-131bef46955c",
            "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
            "name": None,
            "organization": None,
            "status": "unused",
            "username": "globus@globus.org",
        },
        {
            "email": "sirosen@globus.org",
            "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
            "name": "Stephen Rosen",
            "organization": "Globus Team",
            "status": "used",
            "username": "sirosen@globus.org",
        },
    ]
}

IDENTITIES_SINGLE_RESPONSE = {
    "identities": [
        {
            "email": "sirosen@globus.org",
            "id": "ae341a98-d274-11e5-b888-dbae3a8ba545",
            "identity_provider": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
            "name": "Stephen Rosen",
            "organization": "Globus Team",
            "status": "used",
            "username": "sirosen@globus.org",
        }
    ]
}


@pytest.fixture
def client(no_retry_transport):
    class CustomAuthClient(globus_sdk.AuthClient):
        transport_class = no_retry_transport

    return CustomAuthClient()


def test_identity_map(client):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client, ["sirosen@globus.org"])
    assert idmap["sirosen@globus.org"]["organization"] == "Globus Team"

    # lookup by ID also works
    assert (
        idmap["ae341a98-d274-11e5-b888-dbae3a8ba545"]["organization"] == "Globus Team"
    )

    # the last (only) API call was the one by username
    last_req = get_last_request()
    assert "ids" not in last_req.params
    assert last_req.params == {"usernames": "sirosen@globus.org", "provision": "false"}


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
    assert idmap.unresolved_ids == {"ae341a98-d274-11e5-b888-dbae3a8ba545"}
    assert idmap.unresolved_usernames == {"sirosen@globus.org", "globus@globus.org"}


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
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    x = idmap["sirosen@globus.org"]["id"]
    # this is the key: adding it will indicate that we've already seen this ID, perhaps
    # "unintuitively", and that's part of the value of `add()` returning a boolean value
    assert idmap.add(x) is False
    assert idmap[x] == idmap["sirosen@globus.org"]


def test_identity_map_multiple(client):
    register_api_route(
        "auth", ("/v2/api/identities"), json=IDENTITIES_MULTIPLE_RESPONSE
    )
    idmap = globus_sdk.IdentityMap(client, ["sirosen@globus.org", "globus@globus.org"])
    assert idmap["sirosen@globus.org"]["organization"] == "Globus Team"
    assert idmap["globus@globus.org"]["organization"] is None

    last_req = get_last_request()
    # order doesn't matter, but it should be just these two
    # if IdentityMap doesn't deduplicate correctly, it could send
    # `sirosen@globus.org,globus@globus.org,sirosen@globus.org` on the first lookup
    assert last_req.params["usernames"] in [
        "sirosen@globus.org,globus@globus.org",
        "globus@globus.org,sirosen@globus.org",
    ]
    assert last_req.params["provision"] == "false"


def test_identity_map_keyerror(client):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    # a name which doesn't come back, indicating that it was not found, will KeyError
    with pytest.raises(KeyError):
        idmap["sirosen2@globus.org"]

    last_req = get_last_request()
    assert last_req.params == {"usernames": "sirosen2@globus.org", "provision": "false"}


def test_identity_map_get_with_default(client):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    magic = object()  # sentinel value
    idmap = globus_sdk.IdentityMap(client)
    # a name which doesn't come back, if looked up with `get()` should return the
    # default
    assert idmap.get("sirosen2@globus.org", magic) is magic


def test_identity_map_del(client):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    idmap = globus_sdk.IdentityMap(client)
    identity_id = idmap["sirosen@globus.org"]["id"]
    del idmap[identity_id]
    assert idmap.get("sirosen@globus.org")["id"] == identity_id
    # we've only made one request so far
    assert len(responses.calls) == 1
    # but a lookup by ID after a del is going to trigger another request because we've
    # invalidated the cached ID data and are asking the IDMap to look it up again
    assert idmap.get(identity_id)["username"] == "sirosen@globus.org"
    assert len(responses.calls) == 2


@pytest.mark.parametrize(
    "lookup1,lookup2",
    [
        ("sirosen@globus.org", "sirosen@globus.org"),
        ("sirosen@globus.org", "ae341a98-d274-11e5-b888-dbae3a8ba545"),
        ("ae341a98-d274-11e5-b888-dbae3a8ba545", "sirosen@globus.org"),
    ],
)
@pytest.mark.parametrize("initial_add", [True, False])
def test_identity_map_shared_cache_match(client, initial_add, lookup1, lookup2):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_SINGLE_RESPONSE)
    cache = {}
    idmap1 = globus_sdk.IdentityMap(client, cache=cache)
    idmap2 = globus_sdk.IdentityMap(client, cache=cache)
    if initial_add:
        idmap1.add(lookup1)
        idmap2.add(lookup2)
    # no requests yet...
    assert len(responses.calls) == 0
    # do the first lookup, it should make one request
    assert idmap1[lookup1]["organization"] == "Globus Team"
    assert len(responses.calls) == 1
    # lookup more values and make sure that "everything matches"
    assert idmap2[lookup2]["organization"] == "Globus Team"
    assert idmap1[lookup1]["id"] == idmap2[lookup2]["id"]
    assert idmap1[lookup2]["id"] == idmap2[lookup1]["id"]
    # we've only made one request, because the shared cache captured this info on the
    # very first call
    assert len(responses.calls) == 1


@pytest.mark.parametrize(
    "lookup1,lookup2",
    [
        ("sirosen@globus.org", "globus@globus.org"),
        (
            "46bd0f56-e24f-11e5-a510-131bef46955c",
            "ae341a98-d274-11e5-b888-dbae3a8ba545",
        ),
    ],
)
def test_identity_map_shared_cache_mismatch(client, lookup1, lookup2):
    register_api_route("auth", "/v2/api/identities", json=IDENTITIES_MULTIPLE_RESPONSE)
    cache = {}
    idmap1 = globus_sdk.IdentityMap(client, [lookup1, lookup2], cache=cache)
    idmap2 = globus_sdk.IdentityMap(client, cache=cache)
    # no requests yet...
    assert len(responses.calls) == 0
    # do the first lookup, it should make one request
    assert lookup1 in (idmap1[lookup1]["id"], idmap1[lookup1]["username"])
    assert len(responses.calls) == 1
    # lookup more values and make sure that "everything matches"
    assert lookup2 in (idmap2[lookup2]["id"], idmap2[lookup2]["username"])
    assert idmap1[lookup1]["id"] == idmap2[lookup1]["id"]
    assert idmap1[lookup2]["id"] == idmap2[lookup2]["id"]
    # we've only made one request, because the shared cache captured this info on the
    # very first call
    assert len(responses.calls) == 1
