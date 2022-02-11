import importlib
from typing import cast

from .registry import RegisteredResponse, ResponseSet


def load_fixture_set(name: str) -> ResponseSet:
    module = importlib.import_module(f"globus_sdk._testing.data.{name}")
    return cast(ResponseSet, module.RESPONSES)


def load_fixture(
    name: str, *, case: str = "default", replace: bool = False
) -> RegisteredResponse:
    rset = load_fixture_set(name)
    return rset.activate(case, replace=replace)


__all__ = (
    "ResponseSet",
    "RegisteredResponse",
    "load_fixture_set",
    "load_fixture",
)
