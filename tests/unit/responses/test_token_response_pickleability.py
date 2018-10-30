import logging
import os
import pickle
import tempfile

import pytest

import globus_sdk


@pytest.fixture
def auth_client():
    tmplog_handle, tmplog = tempfile.mkstemp()

    client = globus_sdk.AuthClient()
    client.logger.logger.addHandler(logging.FileHandler(tmplog))

    yield client

    try:
        os.remove(tmplog)
    except OSError:
        pass


@pytest.fixture
def token_response(auth_client, make_oauth_token_response):
    return make_oauth_token_response(client=auth_client)


def test_pickle_and_unpickle_no_usage(token_response):
    """
    Test pickle and unpickle, with no usage of the result,
    for all pickle protocol versions supported by the current interpreter.
    """
    pickled_versions = [
        pickle.dumps(token_response, protocol=n)
        for n in range(pickle.HIGHEST_PROTOCOL + 1)
    ]
    unpickled_versions = [pickle.loads(x) for x in pickled_versions]
    for x in unpickled_versions:
        assert x.by_resource_server == token_response.by_resource_server
