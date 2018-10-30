import json
import uuid

import httpretty
import pytest

import globus_sdk
from tests.common import register_api_route


class StringWrapper(object):
    """Simple test object to be a non-string obj wrapping a string"""

    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s


UNAUTHORIZED_RESPONSE_BODY = (
    '{"errors": [{"status": "401", '
    '"id": "cb6a50f8-ac67-11e8-b5fd-0e54e5d1d510", "code": "UNAUTHORIZED", '
    '"detail": "Call must be authenticated", "title": "Unauthorized"}], '
    '"error_description": "Unauthorized", "error": "unauthorized"}'
)

IDENTITIES_SINGLE_RESPONSE = """\
{
  "identities": [
    {
      "email": null,
      "id": "46bd0f56-e24f-11e5-a510-131bef46955c",
      "identity_provider": "7daddf46-70c5-45ee-9f0f-7244fe7c8707",
      "name": null,
      "organization": null,
      "status": "unused",
      "username": "globus@globus.org"
    }
  ]
}"""


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


@pytest.fixture
def identities_single_response():
    register_api_route(
        "auth",
        "/v2/api/identities?usernames=foobar@example.com",
        body=IDENTITIES_SINGLE_RESPONSE,
    )


@pytest.fixture
def identities_multiple_response():
    register_api_route(
        "auth",
        "/v2/api/identities?usernames=foobar@example.com",
        body=IDENTITIES_MULTIPLE_RESPONSE,
    )


@pytest.fixture
def client():
    return globus_sdk.AuthClient()


def test_get_identities_unauthorized(client):
    register_api_route(
        "auth",
        "/v2/api/identities?usernames=foobar@example.com",
        body=UNAUTHORIZED_RESPONSE_BODY,
        status=401,
    )

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        client.get_identities(usernames="foobar@example.com")

    err = excinfo.value
    assert err.code == "UNAUTHORIZED"
    assert err.raw_text == UNAUTHORIZED_RESPONSE_BODY
    assert err.raw_json == json.loads(UNAUTHORIZED_RESPONSE_BODY)


@pytest.mark.parametrize(
    "usernames",
    [
        "globus@globus.org",
        StringWrapper("globus@globus.org"),
        ["globus@globus.org"],
        ("globus@globus.org",),
    ],
)
def test_get_identities_success(usernames, client, identities_single_response):
    res = client.get_identities(usernames=usernames)

    assert res.data == json.loads(IDENTITIES_SINGLE_RESPONSE)

    lastreq = httpretty.last_request()
    assert "usernames" in lastreq.querystring
    assert lastreq.querystring["usernames"] == ["globus@globus.org"]
    # provision defaults to false
    assert "provision" in lastreq.querystring
    assert lastreq.querystring["provision"] == ["false"]


@pytest.mark.parametrize(
    "usernames, expect",
    [
        (
            "globus@globus.org,sirosen@globus.org",
            "globus@globus.org,sirosen@globus.org",
        ),
        (
            (StringWrapper("sirosen@globus.org"), StringWrapper("globus@globus.org")),
            "sirosen@globus.org,globus@globus.org",
        ),
        (
            ["globus@globus.org", "sirosen@globus.org"],
            "globus@globus.org,sirosen@globus.org",
        ),
    ],
)
def test_get_identities_multiple_success(
    usernames, expect, client, identities_multiple_response
):
    res = client.get_identities(usernames=usernames)

    assert res.data == json.loads(IDENTITIES_MULTIPLE_RESPONSE)

    lastreq = httpretty.last_request()
    assert "usernames" in lastreq.querystring
    assert lastreq.querystring["usernames"] == [expect]


@pytest.mark.parametrize(
    "inval, outval",
    [
        (True, "true"),
        (False, "false"),
        (1, "true"),
        (0, "true"),
        ("fALSe", "false"),
        ("true", "true"),
    ],
)
def test_get_identities_provision(inval, outval, client, identities_single_response):
    client.get_identities(usernames="globus@globus.org", provision=inval)
    lastreq = httpretty.last_request()
    assert "provision" in lastreq.querystring
    assert lastreq.querystring["provision"] == [outval]


@pytest.mark.parametrize(
    "ids",
    [
        # two uuids, already comma delimited
        ",".join(
            [
                "46bd0f56-e24f-11e5-a510-131bef46955c",
                "ae341a98-d274-11e5-b888-dbae3a8ba545",
            ]
        ),
        # a list of two UUID objects
        [
            uuid.UUID("46bd0f56-e24f-11e5-a510-131bef46955c"),
            uuid.UUID("ae341a98-d274-11e5-b888-dbae3a8ba545"),
        ],
    ],
)
def test_get_identities_multiple_ids_success(ids, client, identities_multiple_response):
    expect = ",".join(
        ["46bd0f56-e24f-11e5-a510-131bef46955c", "ae341a98-d274-11e5-b888-dbae3a8ba545"]
    )
    res = client.get_identities(ids=ids)

    assert res.data == json.loads(IDENTITIES_MULTIPLE_RESPONSE)

    lastreq = httpretty.last_request()
    assert "ids" in lastreq.querystring
    assert lastreq.querystring["ids"] == [expect]
