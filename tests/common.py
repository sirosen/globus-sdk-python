# -*- coding: utf8 -*-
"""
Common use helpers and utilities for all tests to leverage.
Not so disorganized as a "utils" module and not so refined as a public package.
"""
import inspect
import os
import httpretty
import six
import requests
import json

try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk
from globus_sdk.base import slash_join

# constants

GO_EP1_ID = "ddb59aef-6d04-11e5-ba46-22000b92c6ec"
GO_EP2_ID = "ddb59af0-6d04-11e5-ba46-22000b92c6ec"
# TODO: stop using EP3 once EP1 and EP2 support symlinks
GO_EP3_ID = "4be6107f-634d-11e7-a979-22000bf2d287"
GO_S3_ID = "cf9bcaa5-6d04-11e5-ba46-22000b92c6ec"
GO_EP1_SERVER_ID = 207976

# end constants


def register_api_route(service, path, method=httpretty.GET,
                       adding_headers=None, **kwargs):
    """
    Handy wrapper for adding URIs to the HTTPretty state.
    """
    assert httpretty.is_enabled()
    base_url_map = {
        'auth': 'https://auth.globus.org/',
        'nexus': 'https://nexus.api.globusonline.org/',
        'transfer': 'https://transfer.api.globus.org/v0.10',
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


def register_api_route_fixture_file(service, path, filename, **kwargs):
    """
    register an API route to serve the contents of a file, given the name of
    that file in a `fixture_data` directory, adjacent to the current (calling)
    module

    i.e. in a dir like this:
      path/to/tests
      ├── test_mod.py
      └── fixture_data
          └── dat.txt

    you can call
    >>> register_api_route_fixture_file('transfer', '/foo', 'dat.txt')

    in `test_mod.py`

    it will "do the right thing" and find the abspath to dat.txt , and
    load the contents of that file as the response for '/foo'
    """
    # get calling frame
    frm = inspect.stack()[1]
    # get filename from frame, make it absolute
    modpath = os.path.abspath(frm[1])

    abspath = os.path.join(os.path.dirname(modpath), "fixture_data", filename)
    with open(abspath) as f:
        body = six.b(f.read())

    register_api_route(service, path, body=body, **kwargs)


def make_response(response_class=globus_sdk.GlobusHTTPResponse,
                  status=200, headers=None, json_body=None, text=None):
    """
    Construct and return an SDK response object with a mocked requests.Response

    Unlike mocking of an API route, this is meant for unit testing in which we
    want to directly create the response.
    """
    r = mock.Mock(spec=requests.Response)
    r.status_code = status
    if headers:
        r.headers = headers
    else:
        r.headers = {'Content-Type': 'application/json'}

    if json_body:
        r.json.return_value = json_body
    else:
        r.json.side_effect = ValueError('globus sdk mock value error')

    if text:
        r.text = text
    elif json_body:
        r.text = json.dumps(json_body)
    else:
        r.text = ''

    return response_class(r)
