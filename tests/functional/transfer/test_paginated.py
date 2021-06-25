import json

import pytest
import responses

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
        {"DATA_TYPE": "endpoint", "display_name": f"SDK Test Stub {x}"}
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
            {"DATA_TYPE": "endpoint", "display_name": f"SDK Test Stub {x}"}
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
                "display_name": f"SDK Test Stub {x + 100}",
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
                "display_name": f"SDK Test Stub {x + 200}",
            }
            for x in range(100)
        ],
    },
]


def test_endpoint_search_noresults(client):
    register_api_route("transfer", "/endpoint_search", body=EMPTY_SEARCH_RESULT)

    res = client.endpoint_search("search query!")
    assert res["DATA"] == []


def test_endpoint_search_one_page(client):
    register_api_route(
        "transfer", "/endpoint_search", body=json.dumps(SINGLE_PAGE_SEARCH_RESULT)
    )

    # without calling the paginated version, we only get one page
    res = client.endpoint_search("search query!")
    assert len(list(res)) == 100
    assert res["DATA_TYPE"] == "endpoint_list"
    for res_obj in res:
        assert res_obj["DATA_TYPE"] == "endpoint"


@pytest.mark.parametrize("method", ("__iter__", "pages"))
def test_endpoint_search_multipage(client, method):
    # add each page
    for page in MULTIPAGE_SEARCH_RESULTS:
        register_api_route("transfer", "/endpoint_search", json=page)

    # unpaginated, we'll only get one page
    res = list(client.endpoint_search("search_query"))
    assert len(res) == 100

    # reset and reapply responses
    responses.reset()
    for page in MULTIPAGE_SEARCH_RESULTS:
        register_api_route("transfer", "/endpoint_search", json=page)

    # setup the paginator and either point at `pages()` or directly at the paginator's
    # `__iter__`
    paginator = client.paginated.endpoint_search("search_query")
    if method == "pages":
        iterator = paginator.pages()
    elif method == "__iter__":
        iterator = paginator
    else:
        raise NotImplementedError

    # paginated calls gets all pages
    count_pages = 0
    count_objects = 0
    for page in iterator:
        count_pages += 1
        assert page["DATA_TYPE"] == "endpoint_list"
        for res_obj in page:
            count_objects += 1
            assert res_obj["DATA_TYPE"] == "endpoint"

    assert count_pages == len(MULTIPAGE_SEARCH_RESULTS)
    assert count_objects == sum(len(x["DATA"]) for x in MULTIPAGE_SEARCH_RESULTS)


def test_endpoint_search_multipage_iter_items(client):
    # add each page
    for page in MULTIPAGE_SEARCH_RESULTS:
        register_api_route("transfer", "/endpoint_search", json=page)

    # paginator items() call gets an iterator of individual page items
    paginator = client.paginated.endpoint_search("search_query")
    count_objects = 0
    for item in paginator.items():
        count_objects += 1
        assert item["DATA_TYPE"] == "endpoint"

    assert count_objects == sum(len(x["DATA"]) for x in MULTIPAGE_SEARCH_RESULTS)
