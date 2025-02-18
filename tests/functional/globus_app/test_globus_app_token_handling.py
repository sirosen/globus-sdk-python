import sys
from unittest import mock

import pytest
import responses

import globus_sdk
import globus_sdk.tokenstorage
from globus_sdk._testing import RegisteredResponse, load_response

# the JWT will have a client ID in its audience claim
# make sure to use that value when trying to decode it
CLIENT_ID_FROM_JWT = "7fb58e00-839d-44e3-8047-10a502612dca"


@pytest.fixture(autouse=True)
def _mock_input(capsys, monkeypatch):
    def _fake_input(s):
        print(s)
        return "mock_input"

    monkeypatch.setattr("builtins.input", _fake_input)


@pytest.fixture
def oidc_and_jwk_responses():
    RegisteredResponse(
        service="auth",
        path="/.well-known/openid-configuration",
        method="GET",
        json={
            "issuer": "https://auth.globus.org",
            "authorization_endpoint": "https://auth.globus.org/v2/oauth2/authorize",
            "userinfo_endpoint": "https://auth.globus.org/v2/oauth2/userinfo",
            "token_endpoint": "https://auth.globus.org/v2/oauth2/token",
            "revocation_endpoint": "https://auth.globus.org/v2/oauth2/token/revoke",
            "jwks_uri": "https://auth.globus.org/jwk.json",
            "response_types_supported": [
                "code",
                "token",
                "token id_token",
                "id_token",
            ],
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
        },
    ).add()
    RegisteredResponse(
        service="auth",
        path="/jwk.json",
        method="GET",
        json={
            "keys": [
                {
                    "alg": "RS512",
                    "e": "AQAB",
                    "kty": "RSA",
                    "n": "73l27Yp7WT2c0Ve7EoGJ13AuKzg-GHU7Mpgx0JKa_hO04gAXSVXRadQy7gmdLLtAK8uBVcV0fHGgsBl4J92t-I7hayiJSLbgbX-sZhI_OfegeOLcSNB9poPS9w60XGqR9buYOW2x-KXXitsmyHXNmg_-1u0uqfKHu9pmST8dcjUYXTM5F3oJpQKeJlSH8daMlDks4xb9Y83EEFRv-ppY965-WTm2NW4pwLlbgGTWFvZ6YS6GTb-mfGwGuzStI0lKZ7dOFx9ryYQ4wSoUVHtIrypT-gbuaT90Z2SkwOH-GaEZJkudctBeGpieOsyC7P40UXpwgGNFy3xoWL4vHpnHmQ",  # noqa: E501
                    "use": "sig",
                }
            ]
        },
    ).add()


@pytest.fixture
def token_response():
    RegisteredResponse(
        service="auth",
        path="/v2/oauth2/token",
        method="POST",
        status=200,
        json={
            "access_token": "auth_access_token",
            "scope": "openid",
            "expires_in": 172800,
            "token_type": "Bearer",
            "resource_server": "auth.globus.org",
            # this is a real ID token
            # and since the JWK is real as well, it should decode correctly
            # but it will have a bad expiration time because it's a very old token
            "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJzdWIiOiJjOGFhZDQzZS1kMjc0LTExZTUtYmY5OC04YjAyODk2Y2Y3ODIiLCJvcmdhbml6YXRpb24iOiJHbG9idXMiLCJuYW1lIjoiU3RlcGhlbiBSb3NlbiIsInByZWZlcnJlZF91c2VybmFtZSI6InNpcm9zZW4yQGdsb2J1c2lkLm9yZyIsImlkZW50aXR5X3Byb3ZpZGVyIjoiNDExNDM3NDMtZjNjOC00ZDYwLWJiZGItZWVlY2FiYTg1YmQ5IiwiaWRlbnRpdHlfcHJvdmlkZXJfZGlzcGxheV9uYW1lIjoiR2xvYnVzIElEIiwiZW1haWwiOiJzaXJvc2VuQHVjaGljYWdvLmVkdSIsImxhc3RfYXV0aGVudGljYXRpb24iOjE2MjE0ODEwMDYsImlkZW50aXR5X3NldCI6W3sic3ViIjoiYzhhYWQ0M2UtZDI3NC0xMWU1LWJmOTgtOGIwMjg5NmNmNzgyIiwib3JnYW5pemF0aW9uIjoiR2xvYnVzIiwibmFtZSI6IlN0ZXBoZW4gUm9zZW4iLCJ1c2VybmFtZSI6InNpcm9zZW4yQGdsb2J1c2lkLm9yZyIsImlkZW50aXR5X3Byb3ZpZGVyIjoiNDExNDM3NDMtZjNjOC00ZDYwLWJiZGItZWVlY2FiYTg1YmQ5IiwiaWRlbnRpdHlfcHJvdmlkZXJfZGlzcGxheV9uYW1lIjoiR2xvYnVzIElEIiwiZW1haWwiOiJzaXJvc2VuQHVjaGljYWdvLmVkdSIsImxhc3RfYXV0aGVudGljYXRpb24iOjE2MjE0ODEwMDZ9LHsic3ViIjoiYjZlMjI3ZTgtZGI1Mi0xMWU1LWI2ZmYtYzNiMWNjMjU5ZTBkIiwibmFtZSI6bnVsbCwidXNlcm5hbWUiOiJzaXJvc2VuK2JhZGVtYWlsQGdsb2J1cy5vcmciLCJpZGVudGl0eV9wcm92aWRlciI6IjkyN2Q3MjM4LWY5MTctNGViMi05YWNlLWM1MjNmYTliYTM0ZSIsImlkZW50aXR5X3Byb3ZpZGVyX2Rpc3BsYXlfbmFtZSI6Ikdsb2J1cyBTdGFmZiIsImVtYWlsIjoic2lyb3NlbitiYWRlbWFpbEBnbG9idXMub3JnIiwibGFzdF9hdXRoZW50aWNhdGlvbiI6bnVsbH0seyJzdWIiOiJmN2Y4OWQwYS1kYzllLTExZTUtYWRkMC1hM2NiZDFhNTU5YjMiLCJuYW1lIjpudWxsLCJ1c2VybmFtZSI6InNpcm9zZW4rYmFkZW1haWwyQGdsb2J1cy5vcmciLCJpZGVudGl0eV9wcm92aWRlciI6IjkyN2Q3MjM4LWY5MTctNGViMi05YWNlLWM1MjNmYTliYTM0ZSIsImlkZW50aXR5X3Byb3ZpZGVyX2Rpc3BsYXlfbmFtZSI6Ikdsb2J1cyBTdGFmZiIsImVtYWlsIjoic2lyb3NlbitiYWRlbWFpbDJAZ2xvYnVzLm9yZyIsImxhc3RfYXV0aGVudGljYXRpb24iOm51bGx9XSwiaXNzIjoiaHR0cHM6Ly9hdXRoLmdsb2J1cy5vcmciLCJhdWQiOiI3ZmI1OGUwMC04MzlkLTQ0ZTMtODA0Ny0xMGE1MDI2MTJkY2EiLCJleHAiOjE2MjE2NTM4MTEsImlhdCI6MTYyMTQ4MTAxMSwiYXRfaGFzaCI6IjFQdlVhbmNFdUxfc2cxV1BsNWx1TUVGR2tjTDZQaDh1cWdpVUZzejhkZUEifQ.CtfnFtfM32ICo0euHv9GnpVHFL1jWz0NriPTXAv6w08Ylk9JBJtmB3oMKNSO-1TGoWUPFDp9TFFk6N32VyF0hsVDtT5DT3t5oq0qfqbPrZA3R04HARW0xtcK_ejNDHBmj6wysey3EzjT764XTvcGOe63CKQ_RJm97ulVaseIT0Aet7AYo5tQuOiSOQ70xzL7Oax3W6TrWi3FIAA-PIMSrAJKbsG7imGOVkaIObG9a-X5yTOcrB4IG4Wat-pN_QiCiiOw_LDCF-r455PwalmnSGUugMYfsdL2k3UxqwOMLIppHnx5-UVAzj3mygj8eZTp6imjqxNMdakS3vhG8dtxbw",  # noqa: E501
            "other_tokens": [],
        },
    ).add()


@mock.patch.object(globus_sdk.DefaultIDTokenDecoder, "DEFAULT_JWT_LEEWAY", sys.maxsize)
def test_globus_app_with_default_decoder_only_gets_oidc_data_once(
    oidc_and_jwk_responses, token_response
):
    # needed for logout later
    load_response(globus_sdk.NativeAppAuthClient.oauth2_revoke_token)

    def _count_oidc_calls():
        calls = [c.request for c in responses.calls]
        calls = [
            c
            for c in calls
            if c.url == "https://auth.globus.org/.well-known/openid-configuration"
        ]
        return len(calls)

    def _count_jwk_calls():
        calls = [c.request for c in responses.calls]
        calls = [c for c in calls if c.url == "https://auth.globus.org/jwk.json"]
        return len(calls)

    memory_storage = globus_sdk.tokenstorage.MemoryTokenStorage()
    config = globus_sdk.GlobusAppConfig(token_storage=memory_storage)
    user_app = globus_sdk.UserApp(
        "test-app", config=config, client_id=CLIENT_ID_FROM_JWT
    )

    # start: we haven't made any calls yet
    assert _count_oidc_calls() == 0
    assert _count_jwk_calls() == 0

    # after login: we made one call for each
    user_app.login()
    assert _count_oidc_calls() == 1
    assert _count_jwk_calls() == 1

    # logout and confirm that it was effective
    user_app.logout()
    assert user_app.login_required() is True

    # second login: call counts did not increase
    user_app.login()
    assert _count_oidc_calls() == 1
    assert _count_jwk_calls() == 1
