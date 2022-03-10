import warnings

import globus_sdk

from ._testing import (
    RegisteredResponse,
    ResponseSet,
    get_response_set,
    load_response,
    load_response_set,
    register_response_set,
)

__all__ = (
    "ResponseSet",
    "RegisteredResponse",
    "load_response_set",
    "load_response",
    "get_response_set",
    "register_response_set",
)

if not globus_sdk._DISABLE_TESTING_WARNING:
    warnings.warn("globus_sdk.testing is for internal use only!")
