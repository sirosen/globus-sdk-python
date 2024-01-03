"""
Inspect the signatures of paginated methods and compare them against their
attached paginator requirements.
"""
import inspect

import pytest

import globus_sdk

_CLIENTS_TO_CHECK = []
for attrname in dir(globus_sdk):
    obj = getattr(globus_sdk, attrname)
    if obj is globus_sdk.BaseClient:
        continue
    if isinstance(obj, type) and issubclass(obj, globus_sdk.BaseClient):
        _CLIENTS_TO_CHECK.append(obj)

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

    for param_name in paginator_class._REQUIRES_METHOD_KWARGS:
        assert param_name in kwarg_names, method.__qualname__
