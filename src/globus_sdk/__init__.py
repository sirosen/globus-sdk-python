import logging
import sys
import typing as t

from .version import __version__


def _force_eager_imports() -> None:
    current_module = sys.modules[__name__]

    for attr in __all__:
        getattr(current_module, attr)


if t.TYPE_CHECKING:
    from .authorizers import (
        AccessTokenAuthorizer,
        BasicAuthorizer,
        ClientCredentialsAuthorizer,
        NullAuthorizer,
        RefreshTokenAuthorizer,
    )
    from .client import BaseClient
    from .exc import (
        ErrorSubdocument,
        GlobusAPIError,
        GlobusConnectionError,
        GlobusConnectionTimeoutError,
        GlobusError,
        GlobusSDKUsageError,
        GlobusTimeoutError,
        NetworkError,
        RemovedInV4Warning,
        ValidationError,
    )
    from .globus_app import ClientApp, GlobusApp, GlobusAppConfig, UserApp
    from .local_endpoint import (
        GlobusConnectPersonalOwnerInfo,
        LocalGlobusConnectPersonal,
        LocalGlobusConnectServer,
    )
    from .response import ArrayResponse, GlobusHTTPResponse, IterableResponse
    from .scopes import Scope, ScopeCycleError, ScopeParseError
    from .services.auth import (
        AuthAPIError,
        AuthClient,
        AuthLoginClient,
        ConfidentialAppAuthClient,
        DependentScopeSpec,
        GetConsentsResponse,
        GetIdentitiesResponse,
        IdentityMap,
        NativeAppAuthClient,
        OAuthAuthorizationCodeResponse,
        OAuthClientCredentialsResponse,
        OAuthDependentTokenResponse,
        OAuthRefreshTokenResponse,
        OAuthTokenResponse,
    )
    from .services.compute import (
        ComputeAPIError,
        ComputeClient,
        ComputeClientV2,
        ComputeClientV3,
        ComputeFunctionDocument,
        ComputeFunctionMetadata,
    )
    from .services.flows import (
        FlowsAPIError,
        FlowsClient,
        IterableFlowsResponse,
        SpecificFlowClient,
    )
    from .services.gcs import (
        ActiveScaleStoragePolicies,
        AzureBlobStoragePolicies,
        BlackPearlStoragePolicies,
        BoxStoragePolicies,
        CephStoragePolicies,
        CollectionDocument,
        CollectionPolicies,
        ConnectorTable,
        EndpointDocument,
        GCSAPIError,
        GCSClient,
        GCSRoleDocument,
        GlobusConnectServerConnector,
        GoogleCloudStorageCollectionPolicies,
        GoogleCloudStoragePolicies,
        GoogleDriveStoragePolicies,
        GuestCollectionDocument,
        HPSSStoragePolicies,
        IrodsStoragePolicies,
        IterableGCSResponse,
        MappedCollectionDocument,
        OneDriveStoragePolicies,
        POSIXCollectionPolicies,
        POSIXStagingCollectionPolicies,
        POSIXStagingStoragePolicies,
        POSIXStoragePolicies,
        S3StoragePolicies,
        StorageGatewayDocument,
        StorageGatewayPolicies,
        UnpackingGCSResponse,
        UserCredentialDocument,
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
        SearchQueryV1,
        SearchScrollQuery,
    )
    from .services.timer import TimerAPIError, TimerClient
    from .services.timers import (
        OnceTimerSchedule,
        RecurringTimerSchedule,
        TimerJob,
        TimersAPIError,
        TimersClient,
        TransferTimer,
    )
    from .services.transfer import (
        ActivationRequirementsResponse,
        DeleteData,
        IterableTransferResponse,
        TransferAPIError,
        TransferClient,
        TransferData,
    )
    from .utils import MISSING, MissingType

else:

    def __dir__() -> t.List[str]:
        # dir(globus_sdk) should include everything exported in __all__
        # as well as some explicitly selected attributes from the default dir() output
        # on a module
        #
        # see also:
        # https://discuss.python.org/t/how-to-properly-extend-standard-dir-search-with-module-level-dir/4202
        return list(__all__) + [
            # __all__ itself can be inspected
            "__all__",
            # useful to figure out where a package is installed
            "__file__",
            "__path__",
        ]

    def __getattr__(name: str) -> t.Any:
        from ._lazy_import import load_attr

        if name in __all__:
            value = load_attr(__name__, name)
            setattr(sys.modules[__name__], name, value)
            return value

        raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = (
    "__version__",
    "_force_eager_imports",
    "AccessTokenAuthorizer",
    "ActivationRequirementsResponse",
    "ActiveScaleStoragePolicies",
    "ArrayResponse",
    "AuthAPIError",
    "AuthClient",
    "AuthLoginClient",
    "AzureBlobStoragePolicies",
    "BaseClient",
    "BasicAuthorizer",
    "BatchMembershipActions",
    "BlackPearlStoragePolicies",
    "BoxStoragePolicies",
    "CephStoragePolicies",
    "ClientApp",
    "ClientCredentialsAuthorizer",
    "CollectionDocument",
    "CollectionPolicies",
    "ComputeAPIError",
    "ComputeClient",
    "ComputeClientV2",
    "ComputeClientV3",
    "ComputeFunctionDocument",
    "ComputeFunctionMetadata",
    "ConfidentialAppAuthClient",
    "ConnectorTable",
    "DeleteData",
    "DependentScopeSpec",
    "EndpointDocument",
    "ErrorSubdocument",
    "FlowsAPIError",
    "FlowsClient",
    "GCSAPIError",
    "GCSClient",
    "GCSRoleDocument",
    "GetConsentsResponse",
    "GetIdentitiesResponse",
    "GlobusAPIError",
    "GlobusApp",
    "GlobusAppConfig",
    "GlobusConnectPersonalOwnerInfo",
    "GlobusConnectServerConnector",
    "GlobusConnectionError",
    "GlobusConnectionTimeoutError",
    "GlobusError",
    "GlobusHTTPResponse",
    "GlobusSDKUsageError",
    "GlobusTimeoutError",
    "GoogleCloudStorageCollectionPolicies",
    "GoogleCloudStoragePolicies",
    "GoogleDriveStoragePolicies",
    "GroupMemberVisibility",
    "GroupPolicies",
    "GroupRequiredSignupFields",
    "GroupRole",
    "GroupVisibility",
    "GroupsAPIError",
    "GroupsClient",
    "GroupsManager",
    "GuestCollectionDocument",
    "HPSSStoragePolicies",
    "IdentityMap",
    "IrodsStoragePolicies",
    "IterableFlowsResponse",
    "IterableGCSResponse",
    "IterableResponse",
    "IterableTransferResponse",
    "LocalGlobusConnectPersonal",
    "LocalGlobusConnectServer",
    "MISSING",
    "MappedCollectionDocument",
    "MissingType",
    "NativeAppAuthClient",
    "NetworkError",
    "NullAuthorizer",
    "OAuthAuthorizationCodeResponse",
    "OAuthClientCredentialsResponse",
    "OAuthDependentTokenResponse",
    "OAuthRefreshTokenResponse",
    "OAuthTokenResponse",
    "OnceTimerSchedule",
    "OneDriveStoragePolicies",
    "POSIXCollectionPolicies",
    "POSIXStagingCollectionPolicies",
    "POSIXStagingStoragePolicies",
    "POSIXStoragePolicies",
    "RecurringTimerSchedule",
    "RefreshTokenAuthorizer",
    "RemovedInV4Warning",
    "S3StoragePolicies",
    "Scope",
    "ScopeCycleError",
    "ScopeParseError",
    "SearchAPIError",
    "SearchClient",
    "SearchQuery",
    "SearchQueryV1",
    "SearchScrollQuery",
    "SpecificFlowClient",
    "StorageGatewayDocument",
    "StorageGatewayPolicies",
    "TimerAPIError",
    "TimerClient",
    "TimerJob",
    "TimersAPIError",
    "TimersClient",
    "TransferAPIError",
    "TransferClient",
    "TransferData",
    "TransferTimer",
    "UnpackingGCSResponse",
    "UserApp",
    "UserCredentialDocument",
    "ValidationError",
)


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())
