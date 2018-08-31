import pytest

import globus_sdk

from tests.common import make_response


@pytest.fixture
def oauth_token_response():
    """
    response with conveniently formatted names to help with iteration in tests
    """
    return make_response(
        response_class=globus_sdk.auth.token_response.OAuthTokenResponse,
        json_body={
            "access_token": "access_token_1",
            "expires_in": 3600,
            "id_token": "id_token_value",
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "state": "provided_by_client_to_prevent_replay_attacks",
            "token_type": "bearer",
            "other_tokens": [
                {
                    "access_token": "access_token_2",
                    "expires_in": 3600,
                    "refresh_token": "refresh_token_2",
                    "resource_server": "resource_server_2",
                    "scope": "scope2 scope2:0 scope2:1",
                    "token_type": "bearer"
                },
                {
                    "access_token": "access_token_3",
                    "expires_in": 3600,
                    "refresh_token": "refresh_token_3",
                    "resource_server": "resource_server_3",
                    "scope": "scope3:0 scope3:1",
                    "token_type": "bearer"
                }
            ]
        })


def test_by_resource_server_lookups(oauth_token_response):
    by_rs = oauth_token_response.by_resource_server

    # things which should hold for all
    for n in (1, 2, 3):
        name = 'resource_server_{}'.format(n)
        for attr in ('access_token', 'refresh_token', 'resource_server'):
            assert by_rs[name][attr] == '{}_{}'.format(attr, n)

        assert 'expires_in' not in by_rs[name]
        assert 'expires_at_seconds' in by_rs[name]

        assert by_rs[name]['token_type'] == 'bearer'

    assert by_rs['resource_server_1']['scope'] == 'scope1'
    assert by_rs['resource_server_2']['scope'] == 'scope2 scope2:0 scope2:1'
    assert by_rs['resource_server_3']['scope'] == 'scope3:0 scope3:1'


@pytest.mark.parametrize(
    'scopestr, resource_server',
    [('scope1', 'resource_server_1'),
     ('scope2 scope2:0 scope2:1', 'resource_server_2'),
     ('scope3:0 scope3:1', 'resource_server_3')])
def test_by_scopes_lookups_simple(
        scopestr, resource_server, oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    # containment
    assert scopestr in by_scopes
    for x in scopestr.split():
        assert x in by_scopes

    # maps correctly
    assert by_scopes[scopestr]['resource_server'] == resource_server


def test_by_scopes_lookups_failures(oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    mixed_scopes = 'scope1 scope2'

    # containment
    assert mixed_scopes not in by_scopes
    assert 'badscope' not in by_scopes

    # try to actually do it, ensure KeyErrors have good messages
    with pytest.raises(KeyError) as excinfo:
        by_scopes[mixed_scopes]
    assert 'did not match exactly one token' in str(excinfo.value)

    with pytest.raises(KeyError) as excinfo:
        by_scopes['badscope']
    assert 'was not found' in str(excinfo.value)


def test_by_scopes_lookups_fancy(oauth_token_response):
    by_scopes = oauth_token_response.by_scopes

    # repeated scope
    assert (by_scopes['scope3:0 scope3:0']['resource_server'] ==
            'resource_server_3')

    # not matching order from original document
    assert (by_scopes['scope2:1 scope2 scope2:0']['resource_server'] ==
            'resource_server_2')
