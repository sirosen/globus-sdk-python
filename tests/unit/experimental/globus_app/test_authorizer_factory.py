import time
from unittest import mock

import pytest

from globus_sdk.experimental.globus_app import (
    AccessTokenAuthorizerFactory,
    ClientCredentialsAuthorizerFactory,
    RefreshTokenAuthorizerFactory,
)
from globus_sdk.experimental.globus_app._validating_token_storage import (
    ValidatingTokenStorageHooks,
)
from globus_sdk.experimental.globus_app.errors import (
    ExpiredTokenError,
    MissingTokenError,
)
from globus_sdk.experimental.tokenstorage import TokenStorageData


def make_mock_token_response(token_number=1):
    ret = mock.Mock()
    ret.by_resource_server = {
        "rs1": {
            "resource_server": "rs1",
            "scope": "rs1:all",
            "access_token": f"rs1_access_token_{token_number}",
            "refresh_token": f"rs1_refresh_token_{token_number}",
            "expires_at_seconds": int(time.time()) + 3600,
            "token_type": "Bearer",
        }
    }
    return ret


class MockValidatingTokenStorage:
    def __init__(self):
        self.token_data = {}
        self.scope_requirements = {"rs1": "rs1:all"}
        self.hooks = ValidatingTokenStorageHooks()

    def get_token_data(self, resource_server):
        if resource_server not in self.token_data:
            msg = f"No token data for {resource_server}"
            raise MissingTokenError(msg, resource_server=resource_server)

        token_data = TokenStorageData.from_dict(self.token_data[resource_server])

        self.hooks.before_validate_scope_requirements(resource_server, token_data)

        return token_data

    def store_token_response(self, mock_token_response):
        self.token_data = mock_token_response.by_resource_server


def test_access_token_authorizer_factory():
    initial_response = make_mock_token_response()
    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)
    factory = AccessTokenAuthorizerFactory(token_storage=mock_token_storage)

    # cache is initially empty
    assert factory._authorizer_cache == {}

    # calling get_authorizer once creates a new authorizer from underlying storage
    authorizer = factory.get_authorizer("rs1")
    assert authorizer.get_authorization_header() == "Bearer rs1_access_token_1"

    # calling get_authorizer again gets the same cached authorizer
    authorizer2 = factory.get_authorizer("rs1")
    assert authorizer is authorizer2

    # calling store_token_response_and_clear_cache then get gets a new authorizer
    new_data = make_mock_token_response(token_number=2)
    factory.store_token_response_and_clear_cache(new_data)
    assert factory._authorizer_cache == {}
    authorizer = factory.get_authorizer("rs1")
    assert authorizer.get_authorization_header() == "Bearer rs1_access_token_2"


def test_access_token_authorizer_factory_no_tokens():
    initial_response = make_mock_token_response()
    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)
    factory = AccessTokenAuthorizerFactory(token_storage=mock_token_storage)

    with pytest.raises(MissingTokenError) as exc:
        factory.get_authorizer("rs2")
    assert str(exc.value) == "No token data for rs2"


def test_access_token_authorizer_factory_expired_access_token():
    initial_response = make_mock_token_response()
    initial_response.by_resource_server["rs1"]["expires_at_seconds"] = int(
        time.time() - 3600
    )

    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)
    factory = AccessTokenAuthorizerFactory(token_storage=mock_token_storage)

    with pytest.raises(ExpiredTokenError):
        factory.get_authorizer("rs1")


def test_refresh_token_authorizer_factory():
    initial_response = make_mock_token_response()
    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)

    refresh_data = make_mock_token_response(token_number=2)
    mock_auth_login_client = mock.Mock()
    mock_refresh = mock.Mock()
    mock_refresh.return_value = refresh_data
    mock_auth_login_client.oauth2_refresh_token = mock_refresh

    factory = RefreshTokenAuthorizerFactory(
        token_storage=mock_token_storage,
        auth_login_client=mock_auth_login_client,
    )

    # calling get authorizer creates a new authorizer with existing token data
    authorizer1 = factory.get_authorizer("rs1")
    assert authorizer1.get_authorization_header() == "Bearer rs1_access_token_1"
    assert mock_auth_login_client.oauth2_refresh_token.call_count == 0

    # standard refresh doesn't change the authorizer
    authorizer1._get_new_access_token()
    authorizer2 = factory.get_authorizer("rs1")
    assert authorizer2 is authorizer1
    assert authorizer2.get_authorization_header() == "Bearer rs1_access_token_2"
    assert mock_auth_login_client.oauth2_refresh_token.call_count == 1

    # calling store_token_response_and_clear_cache then get gets a new authorizer
    factory.store_token_response_and_clear_cache(initial_response)
    authorizer3 = factory.get_authorizer("rs1")
    assert authorizer3 is not authorizer1
    assert authorizer3.get_authorization_header() == "Bearer rs1_access_token_1"


def test_refresh_token_authorizer_factory_expired_access_token():
    initial_response = make_mock_token_response()
    initial_response.by_resource_server["rs1"]["expires_at_seconds"] = int(
        time.time() - 3600
    )

    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)

    refresh_data = make_mock_token_response(token_number=2)
    mock_auth_login_client = mock.Mock()
    mock_refresh = mock.Mock()
    mock_refresh.return_value = refresh_data
    mock_auth_login_client.oauth2_refresh_token = mock_refresh

    factory = RefreshTokenAuthorizerFactory(
        token_storage=mock_token_storage,
        auth_login_client=mock_auth_login_client,
    )

    # calling get_authorizer automatically causes a refresh call to get an access token
    authorizer = factory.get_authorizer("rs1")
    assert authorizer.get_authorization_header() == "Bearer rs1_access_token_2"
    assert mock_refresh.call_count == 1


def test_refresh_token_authorizer_factory_no_refresh_token():
    initial_response = make_mock_token_response()
    initial_response.by_resource_server["rs1"]["refresh_token"] = None

    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)

    factory = RefreshTokenAuthorizerFactory(
        token_storage=mock_token_storage,
        auth_login_client=mock.Mock(),
    )

    with pytest.raises(MissingTokenError) as exc:
        factory.get_authorizer("rs1")
    assert str(exc.value) == "No refresh_token for rs1"


def test_client_credentials_authorizer_factory():
    initial_response = make_mock_token_response()
    mock_token_storage = MockValidatingTokenStorage()
    mock_token_storage.store_token_response(initial_response)

    client_token_data = make_mock_token_response(token_number=2)
    mock_confidential_client = mock.Mock()
    mock_client_credentials_tokens = mock.Mock()
    mock_client_credentials_tokens.return_value = client_token_data
    mock_confidential_client.oauth2_client_credentials_tokens = (
        mock_client_credentials_tokens
    )

    factory = ClientCredentialsAuthorizerFactory(
        token_storage=mock_token_storage,
        confidential_client=mock_confidential_client,
    )

    # calling get_authorizer once creates a new authorizer using existing tokens
    authorizer1 = factory.get_authorizer("rs1")
    assert authorizer1.get_authorization_header() == "Bearer rs1_access_token_1"
    assert mock_confidential_client.oauth2_client_credentials_tokens.call_count == 0

    # renewing with existing tokens doesn't change the authorizer
    authorizer1._get_new_access_token()
    authorizer2 = factory.get_authorizer("rs1")
    assert authorizer2 is authorizer1
    assert authorizer2.get_authorization_header() == "Bearer rs1_access_token_2"
    assert mock_confidential_client.oauth2_client_credentials_tokens.call_count == 1

    # calling store_token_response_and_clear_cache then get gets a new authorizer
    factory.store_token_response_and_clear_cache(initial_response)
    authorizer3 = factory.get_authorizer("rs1")
    assert authorizer3 is not authorizer1
    assert authorizer3.get_authorization_header() == "Bearer rs1_access_token_1"


def test_client_credentials_authorizer_factory_no_tokens():
    mock_token_storage = MockValidatingTokenStorage()

    client_token_data = make_mock_token_response()
    mock_confidential_client = mock.Mock()
    mock_client_credentials_tokens = mock.Mock()
    mock_client_credentials_tokens.return_value = client_token_data
    mock_confidential_client.oauth2_client_credentials_tokens = (
        mock_client_credentials_tokens
    )

    factory = ClientCredentialsAuthorizerFactory(
        token_storage=mock_token_storage,
        confidential_client=mock_confidential_client,
    )

    # calling get_authorizer once creates a new authorizer automatically making
    # a client credentials call to get an access token that is then stored
    authorizer = factory.get_authorizer("rs1")
    assert authorizer.get_authorization_header() == "Bearer rs1_access_token_1"
    assert mock_client_credentials_tokens.call_count == 1


def test_client_credentials_authorizer_factory_no_scopes():
    mock_token_storage = MockValidatingTokenStorage()
    mock_confidential_client = mock.Mock()
    factory = ClientCredentialsAuthorizerFactory(
        token_storage=mock_token_storage,
        confidential_client=mock_confidential_client,
    )

    with pytest.raises(ValueError) as exc:
        factory.get_authorizer("rs2")
    assert (
        str(exc.value)
        == "ValidatingTokenStorage has no scope_requirements for resource_server rs2"
    )
