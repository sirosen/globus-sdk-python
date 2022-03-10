import warnings

import globus_sdk

if globus_sdk._ENABLE_TESTING:
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
else:
    warnings.warn("DISABLED")
