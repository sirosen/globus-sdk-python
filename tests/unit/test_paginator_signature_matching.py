"""
Inspect the signatures of paginated methods and compare them against their
attached paginator requirements.
"""

import inspect

import pytest

import globus_sdk
from globus_sdk.paging import (
    HasNextPaginator,
    LastKeyPaginator,
    LimitOffsetTotalPaginator,
    MarkerPaginator,
    NextTokenPaginator,
    NullableMarkerPaginator,
)

_CLIENTS_TO_CHECK = (
    # alphabetical by service name
    # Auth
    globus_sdk.AuthClient,
    globus_sdk.NativeAppAuthClient,
    globus_sdk.ConfidentialAppAuthClient,
    # Flows
    globus_sdk.FlowsClient,
    globus_sdk.SpecificFlowClient,
    # GCS
    globus_sdk.GCSClient,
    # Groups
    globus_sdk.GroupsClient,
    # Search
    globus_sdk.SearchClient,
    # Timers
    globus_sdk.TimerClient,
    # Transfer
    globus_sdk.TransferClient,
)

_METHODS_TO_CHECK = []
for cls in _CLIENTS_TO_CHECK:
    methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    for name, value in methods:
        if name.startswith("_"):
            continue
        # inherited, non-overloaded methods
        if name not in cls.__dict__:
            continue
        if getattr(value, "_has_paginator", False):
            _METHODS_TO_CHECK.append(value)


@pytest.mark.parametrize("method", _METHODS_TO_CHECK)
def test_paginated_method_matches_paginator_requirements(method):
    paginator_class = method._paginator_class

    sig = inspect.signature(method)
    kwarg_names = {
        p.name
        for p in sig.parameters.values()
        if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    }

    if (
        paginator_class is HasNextPaginator
        or paginator_class is LimitOffsetTotalPaginator
    ):
        expect_params = ("limit", "offset")
    elif (
        paginator_class is MarkerPaginator or paginator_class is NullableMarkerPaginator
    ):
        expect_params = ("marker",)
    elif paginator_class is LastKeyPaginator:
        expect_params = ("last_key",)
    elif paginator_class is NextTokenPaginator:
        expect_params = ("next_token",)
    else:
        raise NotImplementedError(f"unrecognized paginator class: {paginator_class}")

    for param_name in expect_params:
        assert param_name in kwarg_names, method.__qualname__
