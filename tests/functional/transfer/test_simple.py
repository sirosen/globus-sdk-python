import json
import uuid

import httpretty
import pytest
import six

import globus_sdk
from tests.common import (
    GO_EP1_ID,
    GO_EP1_SERVER_ID,
    GO_EP2_ID,
    register_api_route_fixture_file,
)


def test_get_endpoint(client):
    """
    Gets endpoint on go#ep1 and go#ep2, validate results
    """
    # register get_endpoint mock data
    register_api_route_fixture_file(
        "transfer", "/endpoint/{}".format(GO_EP1_ID), "get_endpoint_goep1.json"
    )
    register_api_route_fixture_file(
        "transfer", "/endpoint/{}".format(GO_EP2_ID), "get_endpoint_goep2.json"
    )

    # load the tutorial endpoint documents
    ep1_doc = client.get_endpoint(GO_EP1_ID)
    ep2_doc = client.get_endpoint(GO_EP2_ID)

    # check that their contents are at least basically sane (i.e. we didn't
    # get empty dicts or something)
    assert "display_name" in ep1_doc
    assert "display_name" in ep2_doc
    assert "canonical_name" in ep1_doc
    assert "canonical_name" in ep2_doc

    # double check a couple of fields, consider this done
    assert ep1_doc["canonical_name"] == "go#ep1"
    assert ep1_doc["DATA"][0]["id"] == GO_EP1_SERVER_ID
    assert ep2_doc["canonical_name"] == "go#ep2"


def test_update_endpoint(client):
    epid = uuid.uuid1()
    register_api_route_fixture_file(
        "transfer", "/endpoint/{}".format(epid), "ep_update.json", method="PUT"
    )

    # NOTE: pass epid as UUID, not str
    # requires that TransferClient correctly translates it
    update_data = {"display_name": "Updated Name", "description": "Updated description"}
    update_doc = client.update_endpoint(epid, update_data)

    # make sure response is a successful update
    assert update_doc["DATA_TYPE"] == "result"
    assert update_doc["code"] == "Updated"
    assert update_doc["message"] == "Endpoint updated successfully"

    req = httpretty.last_request()
    assert req.body == six.b(json.dumps(update_data))


def test_update_endpoint_rewrites_activation_servers(client):
    """
    Update endpoint, validate results
    """
    epid = "example-id"
    register_api_route_fixture_file(
        "transfer", "/endpoint/{}".format(epid), "ep_create.json", method="PUT"
    )

    # sending myproxy_server implicitly adds oauth_server=null
    update_data = {"myproxy_server": "foo"}
    client.update_endpoint(epid, update_data.copy())
    req = httpretty.last_request()
    assert req.body != six.b(json.dumps(update_data))
    update_data["oauth_server"] = None
    assert req.body == six.b(json.dumps(update_data))

    # sending oauth_server implicitly adds myproxy_server=null
    update_data = {"oauth_server": "foo"}
    client.update_endpoint(epid, update_data.copy())
    req = httpretty.last_request()
    assert req.body != six.b(json.dumps(update_data))
    update_data["myproxy_server"] = None
    assert req.body == six.b(json.dumps(update_data))


def test_update_endpoint_invalid_activation_servers(client):
    epid = "example-id"
    update_data = {"oauth_server": "foo", "myproxy_server": "bar"}
    with pytest.raises(globus_sdk.GlobusSDKUsageError) as excinfo:
        client.update_endpoint(epid, update_data)

    assert "either MyProxy or OAuth, not both" in str(excinfo.value)


def test_create_endpoint(client):
    register_api_route_fixture_file(
        "transfer", "/endpoint", "ep_create.json", method="POST"
    )

    create_data = {"display_name": "Name", "description": "desc"}
    create_doc = client.create_endpoint(create_data)

    # make sure response is a successful update
    assert create_doc["DATA_TYPE"] == "endpoint_create_result"
    assert create_doc["code"] == "Created"
    assert create_doc["message"] == "Endpoint created successfully"

    req = httpretty.last_request()
    assert req.body == six.b(json.dumps(create_data))


def test_create_endpoint_invalid_activation_servers(client):
    create_data = {"oauth_server": "foo", "myproxy_server": "bar"}
    with pytest.raises(globus_sdk.GlobusSDKUsageError) as excinfo:
        client.create_endpoint(create_data)

    assert "either MyProxy or OAuth, not both" in str(excinfo.value)
