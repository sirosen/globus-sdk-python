import urllib.parse

import pytest

from globus_sdk import MISSING
from globus_sdk.testing import get_last_request, load_response


@pytest.mark.parametrize("filter_states", [MISSING, "open"])
@pytest.mark.parametrize("filter_roles", [MISSING, "viewer"])
@pytest.mark.parametrize("orderby", [MISSING, "created_timestamp ASC"])
def test_list_web_inputs_simple(flows_client, filter_states, filter_roles, orderby):
    meta = load_response(flows_client.list_web_inputs).metadata

    add_kwargs = {}
    if filter_states is not MISSING:
        add_kwargs["filter_states"] = filter_states
    if filter_roles is not MISSING:
        add_kwargs["filter_roles"] = filter_roles
    if orderby is not MISSING:
        add_kwargs["orderby"] = orderby

    res = flows_client.list_web_inputs(**add_kwargs)

    assert res.http_status == 200
    # dict-like indexing
    assert meta["first_web_input_id"] == res["web_input_summaries"][0]["id"]
    # list conversion (using __iter__) and indexing
    assert meta["first_web_input_id"] == list(res)[0]["id"]

    req = get_last_request()
    assert req.body is None
    parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(req.url).query)
    expect_query_params = {
        k: [v]
        for k, v in (
            ("filter_states", filter_states),
            ("filter_roles", filter_roles),
            ("orderby", orderby),
        )
        if v is not MISSING
    }
    assert parsed_qs == expect_query_params


@pytest.mark.parametrize("by_pages", [True, False])
def test_list_web_inputs_paginated(flows_client, by_pages):
    meta = load_response(flows_client.list_web_inputs, case="paginated").metadata
    total_items = meta["total_items"]
    num_pages = meta["num_pages"]
    expect_markers = meta["expect_markers"]

    res = flows_client.paginated.list_web_inputs()
    if by_pages:
        pages = list(res)
        assert len(pages) == num_pages
        for i, page in enumerate(pages):
            assert page["marker"] == expect_markers[i]
    else:
        items = list(res.items())
        assert len(items) == total_items
