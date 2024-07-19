import urllib.parse

import pytest

from globus_sdk._testing import get_last_request, load_response


@pytest.mark.parametrize(
    "client_kwargs, qs",
    [
        ({}, {}),
        ({"query_params": {"foo": "bar"}}, {"foo": "bar"}),
        ({"filter": "foo"}, {"filter": "foo"}),
        ({"limit": 10, "offset": 100}, {"limit": "10", "offset": "100"}),
        ({"limit": 10, "query_params": {"limit": 100}}, {"limit": "10"}),
        ({"filter": "foo:bar:baz"}, {"filter": "foo:bar:baz"}),
        ({"filter": {"foo": "bar", "bar": "baz"}}, {"filter": "foo:bar/bar:baz"}),
        ({"filter": {"foo": ["bar", "baz"]}}, {"filter": "foo:bar,baz"}),
    ],
)
def test_task_list(client, client_kwargs, qs):
    load_response(client.task_list)
    client.task_list(**client_kwargs)

    req = get_last_request()
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    # parsed_qs will have each value as a list (because query-params are a multidict)
    # so transform the test data to match before comparison
    assert parsed_qs == {k: [v] for k, v in qs.items()}
