from .registry import (
    RegisteredResponse,
    ResponseSet,
    get_response_set,
    register_response_set,
)


def load_response_set(name: str) -> ResponseSet:
    ret = get_response_set(name)
    ret.activate_all()
    return ret


def load_response(
    name: str, *, case: str = "default", replace: bool = False
) -> RegisteredResponse:
    rset = get_response_set(name)
    return rset.activate(case, replace=replace)


__all__ = (
    "ResponseSet",
    "RegisteredResponse",
    "load_response_set",
    "load_response",
    "get_response_set",
    "register_response_set",
)
