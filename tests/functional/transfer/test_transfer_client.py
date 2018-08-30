import pytest

import globus_sdk

from tests.common import (GO_EP1_ID, GO_EP2_ID, GO_EP1_SERVER_ID,

                          register_api_route_fixture_file)


@pytest.fixture
def client():
    return globus_sdk.TransferClient()


def test_get_endpoint(client):
    """
    Gets endpoint on go#ep1 and go#ep2, validate results
    """
    # register get_endpoint mock data
    register_api_route_fixture_file(
        'transfer', '/endpoint/{}'.format(GO_EP1_ID),
        'get_endpoint_goep1.json')
    register_api_route_fixture_file(
        'transfer', '/endpoint/{}'.format(GO_EP2_ID),
        'get_endpoint_goep2.json')

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
    assert ep1_doc["DATA"][0]['id'] == GO_EP1_SERVER_ID
    assert ep2_doc["canonical_name"] == "go#ep2"
