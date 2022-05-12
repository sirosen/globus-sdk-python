import importlib
import logging
import typing

from .version import __version__

_LAZY_IMPORT_TABLE = {
    "authorizers": (
        "AccessTokenAuthorizer",
        "BasicAuthorizer",
        "ClientCredentialsAuthorizer",
        "NullAuthorizer",
        "RefreshTokenAuthorizer",
    ),
    "client": ("BaseClient",),
    "exc": (
        "GlobusAPIError",
        "GlobusConnectionError",
        "GlobusConnectionTimeoutError",
        "GlobusError",
        "GlobusSDKUsageError",
        "GlobusTimeoutError",
        "NetworkError",
    ),
    "local_endpoint": (
        "GlobusConnectPersonalOwnerInfo",
        "LocalGlobusConnectPersonal",
    ),
    "response": ("GlobusHTTPResponse",),
    "services.auth": (
        "AuthAPIError",
        "AuthClient",
        "ConfidentialAppAuthClient",
        "IdentityMap",
        "NativeAppAuthClient",
        "OAuthDependentTokenResponse",
        "OAuthTokenResponse",
    ),
    "services.gcs": (
        "CollectionDocument",
        "GCSAPIError",
        "GCSClient",
        "GCSRoleDocument",
        "GuestCollectionDocument",
        "MappedCollectionDocument",
    ),
    "services.groups": (
        "BatchMembershipActions",
        "GroupMemberVisibility",
        "GroupPolicies",
        "GroupRequiredSignupFields",
        "GroupRole",
        "GroupsAPIError",
        "GroupsClient",
        "GroupsManager",
        "GroupVisibility",
    ),
    "services.search": (
        "SearchAPIError",
        "SearchClient",
        "SearchQuery",
        "SearchScrollQuery",
    ),
    "services.timer": ("TimerAPIError", "TimerClient", "TimerJob"),
    "services.transfer": (
        "ActivationRequirementsResponse",
        "DeleteData",
        "IterableTransferResponse",
        "TransferAPIError",
        "TransferClient",
        "TransferData",
    ),
}

if typing.TYPE_CHECKING:
    from .authorizers import (
        AccessTokenAuthorizer,
        BasicAuthorizer,
        ClientCredentialsAuthorizer,
        NullAuthorizer,
        RefreshTokenAuthorizer,
    )
    from .client import BaseClient
    from .exc import (
        GlobusAPIError,
        GlobusConnectionError,
        GlobusConnectionTimeoutError,
        GlobusError,
        GlobusSDKUsageError,
        GlobusTimeoutError,
        NetworkError,
    )
    from .local_endpoint import (
        GlobusConnectPersonalOwnerInfo,
        LocalGlobusConnectPersonal,
    )
    from .response import GlobusHTTPResponse
    from .services.auth import (
        AuthAPIError,
        AuthClient,
        ConfidentialAppAuthClient,
        IdentityMap,
        NativeAppAuthClient,
        OAuthDependentTokenResponse,
        OAuthTokenResponse,
    )
    from .services.gcs import (
        CollectionDocument,
        GCSAPIError,
        GCSClient,
        GCSRoleDocument,
        GuestCollectionDocument,
        MappedCollectionDocument,
    )
    from .services.groups import (
        BatchMembershipActions,
        GroupMemberVisibility,
        GroupPolicies,
        GroupRequiredSignupFields,
        GroupRole,
        GroupsAPIError,
        GroupsClient,
        GroupsManager,
        GroupVisibility,
    )
    from .services.search import (
        SearchAPIError,
        SearchClient,
        SearchQuery,
        SearchScrollQuery,
    )
    from .services.timer import TimerAPIError, TimerClient, TimerJob
    from .services.transfer import (
        ActivationRequirementsResponse,
        DeleteData,
        IterableTransferResponse,
        TransferAPIError,
        TransferClient,
        TransferData,
    )
else:

    def __getattr__(name: str) -> typing.Any:
        for modname, items in _LAZY_IMPORT_TABLE.items():
            if name in items:
                mod = importlib.import_module("." + modname, __name__)
                return getattr(mod, name)

        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = (
    "AccessTokenAuthorizer",
    "BasicAuthorizer",
    "ClientCredentialsAuthorizer",
    "NullAuthorizer",
    "RefreshTokenAuthorizer",
    "BaseClient",
    "GlobusAPIError",
    "GlobusConnectionError",
    "GlobusConnectionTimeoutError",
    "GlobusError",
    "GlobusSDKUsageError",
    "GlobusTimeoutError",
    "NetworkError",
    "GlobusConnectPersonalOwnerInfo",
    "LocalGlobusConnectPersonal",
    "GlobusHTTPResponse",
    "AuthAPIError",
    "AuthClient",
    "ConfidentialAppAuthClient",
    "IdentityMap",
    "NativeAppAuthClient",
    "OAuthDependentTokenResponse",
    "OAuthTokenResponse",
    "CollectionDocument",
    "GCSAPIError",
    "GCSClient",
    "GCSRoleDocument",
    "GuestCollectionDocument",
    "MappedCollectionDocument",
    "BatchMembershipActions",
    "GroupMemberVisibility",
    "GroupPolicies",
    "GroupRequiredSignupFields",
    "GroupRole",
    "GroupsAPIError",
    "GroupsClient",
    "GroupsManager",
    "GroupVisibility",
    "SearchAPIError",
    "SearchClient",
    "SearchQuery",
    "SearchScrollQuery",
    "TimerAPIError",
    "TimerClient",
    "TimerJob",
    "ActivationRequirementsResponse",
    "DeleteData",
    "IterableTransferResponse",
    "TransferAPIError",
    "TransferClient",
    "TransferData",
)

# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())
