from globus_sdk._testing.registry import RegisteredResponse, ResponseSet

GO_EP1_ID = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"


RESPONSES = ResponseSet(
    autoactivate=RegisteredResponse(
        "transfer",
        f"/endpoint/{GO_EP1_ID}/autoactivate",
        method="POST",
        status=401,
        json={
            "code": "ClientError.AuthenticationFailed",
            "message": "foo bar",
            "request_id": "abc123",
        },
        metadata={"request_id": "abc123"},
    ),
)
