from globus_sdk._testing.registry import RegisteredResponse, ResponseSet

from ._common import ERROR_ID, UNAUTHORIZED_AUTH_RESPONSE_JSON

RESPONSES = ResponseSet(
    unauthorized=RegisteredResponse(
        service="auth",
        path="/v2/oauth2/userinfo",
        status=401,
        json=UNAUTHORIZED_AUTH_RESPONSE_JSON,
        metadata={"error_id": ERROR_ID},
    ),
)