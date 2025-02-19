import uuid
from unittest import mock

import pytest
import requests

import globus_sdk


class MockDecoder(globus_sdk.IDTokenDecoder):
    def get_openid_configuration(self):
        return {
            "issuer": "https://auth.globus.org",
            "authorization_endpoint": "https://auth.globus.org/v2/oauth2/authorize",
            "userinfo_endpoint": "https://auth.globus.org/v2/oauth2/userinfo",
            "token_endpoint": "https://auth.globus.org/v2/oauth2/token",
            "revocation_endpoint": "https://auth.globus.org/v2/oauth2/token/revoke",
            "jwks_uri": "https://auth.globus.org/jwk.json",
            "response_types_supported": ["code", "token", "token id_token", "id_token"],
            "id_token_signing_alg_values_supported": ["RS512"],
            "scopes_supported": ["openid", "email", "profile"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
            "claims_supported": [
                "at_hash",
                "aud",
                "email",
                "exp",
                "name",
                "nonce",
                "preferred_username",
                "iat",
                "iss",
                "sub",
            ],
            "subject_types_supported": ["public"],
        }

    def get_jwk(self):
        return mock.Mock()


@pytest.mark.parametrize(
    "default_audience_callable, expect_value",
    (
        pytest.param(None, None, id="no-override"),
        pytest.param(lambda *_, **__: None, None, id="explicit-none"),
        pytest.param(lambda *_, **__: "myaud", "myaud", id="myaud"),
    ),
)
def test_decoding_passes_default_audience(default_audience_callable, expect_value):
    class MyDecoder(MockDecoder):
        pass

    if default_audience_callable is not None:
        MyDecoder.default_audience = property(default_audience_callable)

    decoder = MyDecoder()
    assert decoder.default_audience == expect_value

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("")
        assert mock_jwt_decode.call_args.kwargs["audience"] == expect_value


def test_decoding_can_pass_explicit_audience():
    decoder = MockDecoder()

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("", audience="myaud")
        assert mock_jwt_decode.call_args.kwargs["audience"] == "myaud"


def test_default_encoder_derives_audience_from_client():
    client = mock.Mock()
    client.client_id = uuid.uuid1()

    decoder = globus_sdk.DefaultIDTokenDecoder(client)
    assert decoder.default_audience == client.client_id

    # delattr on a mock removes an attribute and ensures that a `hasattr` check on
    # it will return False (the default is for any attribute to return True)
    delattr(client, "client_id")

    assert decoder.default_audience is None


def test_setting_oidc_config_on_default_decoder_unpacks_data():
    oidc_config = {"x": 1}
    raw_response = mock.Mock(spec=requests.Response)
    raw_response.json.return_value = oidc_config
    response = globus_sdk.GlobusHTTPResponse(raw_response, client=mock.Mock())

    decoder = globus_sdk.DefaultIDTokenDecoder(mock.Mock())
    decoder.store_openid_configuration(response)

    assert decoder.get_openid_configuration() == oidc_config


def test_default_jwt_leeway_can_be_overridden_on_call():
    default_leeway = globus_sdk.IDTokenDecoder.DEFAULT_JWT_LEEWAY
    decoder = MockDecoder()

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("", leeway=int(default_leeway * 2))
        assert mock_jwt_decode.call_args.kwargs["leeway"] == int(default_leeway * 2)


def test_default_jwt_leeway_can_be_overridden_via_subclass():
    default_leeway = globus_sdk.IDTokenDecoder.DEFAULT_JWT_LEEWAY

    class MyDecoder(MockDecoder):
        DEFAULT_JWT_LEEWAY = int(default_leeway * 2)

    decoder = MyDecoder()

    with mock.patch("jwt.decode") as mock_jwt_decode:
        decoder.decode("")
        assert mock_jwt_decode.call_args.kwargs["leeway"] == int(default_leeway * 2)
