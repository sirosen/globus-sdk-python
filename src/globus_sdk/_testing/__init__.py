from typing import Any

from .registry import (
    RegisteredResponse,
    ResponseSet,
    get_response_set,
    register_response_set,
)


def load_response_set(set_id: Any) -> ResponseSet:
    ret = get_response_set(set_id)
    ret.activate_all()
    return ret


def load_response(set_id: Any, *, case: str = "default") -> RegisteredResponse:
    rset = get_response_set(set_id)
    return rset.activate(case)


__all__ = (
    "ResponseSet",
    "RegisteredResponse",
    "load_response_set",
    "load_response",
    "get_response_set",
    "register_response_set",
)
