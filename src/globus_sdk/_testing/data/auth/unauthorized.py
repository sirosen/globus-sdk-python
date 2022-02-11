from globus_sdk._testing.registry import RegisteredResponse, ResponseSet

_auth_response_json = {
    "errors": [
        {
            "status": "401",
            "id": "cb6a50f8-ac67-11e8-b5fd-0e54e5d1d510",
            "code": "UNAUTHORIZED",
            "detail": "Call must be authenticated",
            "title": "Unauthorized",
        }
    ],
    "error_description": "Unauthorized",
    "error": "unauthorized",
}

RESPONSES = ResponseSet(
    userinfo=RegisteredResponse(
        "auth",
        "/v2/oauth2/userinfo",
        status=401,
        json=_auth_response_json,
        metadata={"error_id": "cb6a50f8-ac67-11e8-b5fd-0e54e5d1d510"},
    ),
    get_identities=RegisteredResponse(
        "auth",
        "/v2/api/identities",
        status=401,
        json=_auth_response_json,
        metadata={"error_id": "cb6a50f8-ac67-11e8-b5fd-0e54e5d1d510"},
    ),
)
