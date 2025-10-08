"""
Unit tests for globus_sdk.SearchQueryV1
"""

from globus_sdk import MISSING, SearchQueryV1


def test_init_v1():
    query = SearchQueryV1()

    # ensure the version is set to query#1.0.0
    assert query["@version"] == "query#1.0.0"

    # ensure key attributes initialize to empty lists
    for attribute in ["facets", "filters", "post_facet_filters", "sort", "boosts"]:
        assert query[attribute] == MISSING

    # init with supported fields
    params = {"q": "foo", "limit": 10, "offset": 0, "advanced": False}
    param_query = SearchQueryV1(**params)
    for par in params:
        assert param_query[par] == params[par]

    # init with additional_fields
    add_params = {"param1": "value1", "param2": "value2"}
    param_query = SearchQueryV1(additional_fields=add_params)
    for par in add_params:
        assert param_query[par] == add_params[par]
