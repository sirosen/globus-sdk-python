import pytest
from six.moves.urllib.parse import quote_plus

import globus_sdk
from globus_sdk.auth.oauth2_constants import DEFAULT_REQUESTED_SCOPES
from globus_sdk.auth.oauth2_native_app import make_native_app_challenge
from tests.common import register_api_route

CLIENT_ID = "d0f1d9b0-bd81-4108-be74-ea981664453a"
INVALID_GRANT_RESPONSE_BODY = '{"error":"invalid_grant"}'


def test_oauth2_get_authorize_url_native():
    """
    Starts an auth flow with a NativeAppFlowManager, gets the authorize url
    validates expected results with both default and specified parameters.
    """
    ac = globus_sdk.AuthClient(client_id=CLIENT_ID)

    # default parameters for starting auth flow
    flow_manager = globus_sdk.auth.GlobusNativeAppFlowManager(ac)
    ac.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = ac.oauth2_get_authorize_url()
    expected_vals = [
        ac.base_url + "v2/oauth2/authorize?",
        "client_id=" + ac.client_id,
        "redirect_uri=" + quote_plus(ac.base_url + "v2/web/auth-code"),
        "scope=" + quote_plus(" ".join(DEFAULT_REQUESTED_SCOPES)),
        "state=" + "_default",
        "response_type=" + "code",
        "code_challenge=" + quote_plus(flow_manager.challenge),
        "code_challenge_method=" + "S256",
        "access_type=" + "online",
    ]
    for val in expected_vals:
        assert val in url_res

    # starting flow with specified paramaters
    flow_manager = globus_sdk.auth.GlobusNativeAppFlowManager(
        ac,
        requested_scopes="scopes",
        redirect_uri="uri",
        state="state",
        verifier=("a" * 43),
        refresh_tokens=True,
    )
    ac.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = ac.oauth2_get_authorize_url()
    verifier, remade_challenge = make_native_app_challenge("a" * 43)
    expected_vals = [
        ac.base_url + "v2/oauth2/authorize?",
        "client_id=" + ac.client_id,
        "redirect_uri=" + "uri",
        "scope=" + "scopes",
        "state=" + "state",
        "response_type=" + "code",
        "code_challenge=" + quote_plus(remade_challenge),
        "code_challenge_method=" + "S256",
        "access_type=" + "offline",
    ]
    for val in expected_vals:
        assert val in url_res


def test_oauth2_get_authorize_url_confidential():
    """
    Starts an auth flow with a AuthorizationCodeFlowManager, gets the
    authorize url, validates expected results with both default and specified
    parameters.
    """
    ac = globus_sdk.AuthClient(client_id=CLIENT_ID)

    # default parameters for starting auth flow
    flow_manager = globus_sdk.auth.GlobusAuthorizationCodeFlowManager(ac, "uri")
    ac.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = ac.oauth2_get_authorize_url()
    expected_vals = [
        ac.base_url + "v2/oauth2/authorize?",
        "client_id=" + ac.client_id,
        "redirect_uri=" + "uri",
        "scope=" + quote_plus(" ".join(DEFAULT_REQUESTED_SCOPES)),
        "state=" + "_default",
        "response_type=" + "code",
        "access_type=" + "online",
    ]

    for val in expected_vals:
        assert val in url_res

    # starting flow with specified paramaters
    flow_manager = globus_sdk.auth.GlobusAuthorizationCodeFlowManager(
        ac,
        requested_scopes="scopes",
        redirect_uri="uri",
        state="state",
        refresh_tokens=True,
    )
    ac.current_oauth2_flow_manager = flow_manager

    # get url_and validate results
    url_res = ac.oauth2_get_authorize_url()
    expected_vals = [
        ac.base_url + "v2/oauth2/authorize?",
        "client_id=" + ac.client_id,
        "redirect_uri=" + "uri",
        "scope=" + "scopes",
        "state=" + "state",
        "response_type=" + "code",
        "access_type=" + "offline",
    ]
    for val in expected_vals:
        assert val in url_res


def test_oauth2_exchange_code_for_tokens_native():
    """
    Starts a NativeAppFlowManager, Confirms invalid code raises 401
    Further testing cannot be done without user login credentials
    """
    register_api_route(
        "auth",
        "/v2/oauth2/token",
        method="POST",
        body=INVALID_GRANT_RESPONSE_BODY,
        status=401,
    )

    ac = globus_sdk.AuthClient(client_id=CLIENT_ID)
    flow_manager = globus_sdk.auth.GlobusNativeAppFlowManager(ac)
    ac.current_oauth2_flow_manager = flow_manager

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        ac.oauth2_exchange_code_for_tokens("invalid_code")
    assert excinfo.value.http_status == 401
    assert excinfo.value.code == "Error"


def test_oauth2_exchange_code_for_tokens_confidential():
    """
    Starts an AuthorizationCodeFlowManager, Confirms bad code raises 401
    Further testing cannot be done without user login credentials
    """
    register_api_route(
        "auth",
        "/v2/oauth2/token",
        method="POST",
        body=INVALID_GRANT_RESPONSE_BODY,
        status=401,
    )

    ac = globus_sdk.AuthClient(client_id=CLIENT_ID)
    flow_manager = globus_sdk.auth.GlobusAuthorizationCodeFlowManager(ac, "uri")
    ac.current_oauth2_flow_manager = flow_manager

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        ac.oauth2_exchange_code_for_tokens("invalid_code")
    assert excinfo.value.http_status == 401
    assert excinfo.value.code == "Error"
