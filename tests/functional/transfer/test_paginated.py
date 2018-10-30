"""
Tests for PaginatedResource responses from TransferClient
"""
import json

import httpretty
import pytest

from tests.common import register_api_route

# empty search
EMPTY_SEARCH_RESULT = """{
  "DATA_TYPE": "endpoint_list",
  "offset": 0,
  "limit": 100,
  "has_next_page": false,
  "DATA": [
  ]
}"""

# single page of data
SINGLE_PAGE_SEARCH_RESULT = {
    "DATA_TYPE": "endpoint_list",
    "offset": 0,
    "limit": 100,
    "has_next_page": False,
    "DATA": [
        {"DATA_TYPE": "endpoint", "display_name": "SDK Test Stub {}".format(x)}
        for x in range(100)
    ],
}

# multiple pages of results, very stubby
MULTIPAGE_SEARCH_RESULTS = [
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 0,
        "limit": 100,
        "has_next_page": True,
        "DATA": [
            {"DATA_TYPE": "endpoint", "display_name": "SDK Test Stub {}".format(x)}
            for x in range(100)
        ],
    },
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 100,
        "limit": 100,
        "has_next_page": True,
        "DATA": [
            {
                "DATA_TYPE": "endpoint",
                "display_name": "SDK Test Stub {}".format(x + 100),
            }
            for x in range(100)
        ],
    },
    {
        "DATA_TYPE": "endpoint_list",
        "offset": 200,
        "limit": 100,
        "has_next_page": False,
        "DATA": [
            {
                "DATA_TYPE": "endpoint",
                "display_name": "SDK Test Stub {}".format(x + 200),
            }
            for x in range(100)
        ],
    },
]


def test_endpoint_search_noresults(client):
    register_api_route("transfer", "/endpoint_search", body=EMPTY_SEARCH_RESULT)

    res = client.endpoint_search("search query!")
    assert res.data == []


def test_endpoint_search_one_page(client):
    register_api_route(
        "transfer", "/endpoint_search", body=json.dumps(SINGLE_PAGE_SEARCH_RESULT)
    )

    # without cranking up num_results, we'll only get 25
    res = client.endpoint_search("search query!")
    assert len(list(res)) == 25

    # paginated results don't have __getitem__ !
    # attempting to __getitem__ on a response object defaults to a TypeError
    with pytest.raises(TypeError):
        res["DATA_TYPE"]

    # second fetch is empty
    assert list(res) == []

    # reload
    res = client.endpoint_search("search query!")
    for res_obj in res:
        assert res_obj["DATA_TYPE"] == "endpoint"


def test_endpoint_search_reduced(client):
    register_api_route(
        "transfer", "/endpoint_search", body=json.dumps(SINGLE_PAGE_SEARCH_RESULT)
    )

    # result has 100 items -- num_results caps it even if the API
    # returns more
    res = client.endpoint_search("search query!", num_results=10)
    assert len(list(res)) == 10


def test_endpoint_search_multipage(client):
    pages = [json.dumps(x) for x in MULTIPAGE_SEARCH_RESULTS]
    responses = [httpretty.Response(p) for p in pages]

    register_api_route("transfer", "/endpoint_search", responses=responses)

    # without cranking up num_results, we'll only get 25
    res = list(client.endpoint_search("search_query"))
    assert len(res) == 25

    # reapply (resets responses)
    register_api_route("transfer", "/endpoint_search", responses=responses)

    # num_results=None -> no limit
    res = list(client.endpoint_search("search_query", num_results=None))
    assert res[-1]["display_name"] == "SDK Test Stub 299"
    assert len(res) == sum(len(x["DATA"]) for x in MULTIPAGE_SEARCH_RESULTS)
