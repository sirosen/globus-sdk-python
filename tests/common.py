"""
Common use helpers and utilities for all tests to leverage.
Not so disorganized as a "utils" module and not so refined as a public package.
"""
import httpretty

from globus_sdk.base import slash_join


def register_api_route(service, path, method=httpretty.GET,
                       adding_headers=None, **kwargs):
    """
    Handy wrapper for adding URIs to the HTTPretty state.
    """
    assert httpretty.is_enabled()
    base_url_map = {
        'auth': 'https://auth.globus.org/',
        'nexus': 'https://nexus.api.globusonline.org/',
        'transfer': 'https://transfer.api.globus.org/',
        'search': 'https://search.api.globus.org/'
    }
    assert service in base_url_map
    base_url = base_url_map.get(service)
    full_url = slash_join(base_url, path)

    # can set it to `{}` explicitly to clear the default
    if adding_headers is None:
        adding_headers = {'Content-Type': 'application/json'}

    httpretty.register_uri(method, full_url, adding_headers=adding_headers,
                           **kwargs)
