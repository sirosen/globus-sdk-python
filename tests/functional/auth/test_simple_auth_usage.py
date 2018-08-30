import json
import pytest

import globus_sdk

from tests.common import register_api_route


UNAUTHORIZED_RESPONSE_BODY = (
    '{"errors": [{"status": "401", '
    '"id": "cb6a50f8-ac67-11e8-b5fd-0e54e5d1d510", "code": "UNAUTHORIZED", '
    '"detail": "Call must be authenticated", "title": "Unauthorized"}], '
    '"error_description": "Unauthorized", "error": "unauthorized"}')


def test_get_identities_unauthorized():
    register_api_route(
        'auth', '/v2/api/identities?usernames=foobar@example.com',
        body=UNAUTHORIZED_RESPONSE_BODY,
        status=401)
    ac = globus_sdk.AuthClient()

    with pytest.raises(globus_sdk.AuthAPIError) as excinfo:
        ac.get_identities(usernames='foobar@example.com')

    err = excinfo.value

    assert err.code == 'UNAUTHORIZED'
    assert err.raw_text == UNAUTHORIZED_RESPONSE_BODY
    assert err.raw_json == json.loads(UNAUTHORIZED_RESPONSE_BODY)
