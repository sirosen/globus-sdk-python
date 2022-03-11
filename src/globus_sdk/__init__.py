import logging
import os

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
from .local_endpoint import GlobusConnectPersonalOwnerInfo, LocalGlobusConnectPersonal
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
from .services.transfer import (
    ActivationRequirementsResponse,
    DeleteData,
    IterableTransferResponse,
    TransferAPIError,
    TransferClient,
    TransferData,
)
from .version import __version__

__all__ = (
    "__version__",
    "BaseClient",
    "GlobusHTTPResponse",
    "GlobusError",
    "GlobusSDKUsageError",
    "GlobusAPIError",
    "AuthAPIError",
    "TransferAPIError",
    "SearchAPIError",
    "GroupsAPIError",
    "NetworkError",
    "GlobusConnectionError",
    "GlobusTimeoutError",
    "GlobusConnectionTimeoutError",
    "NullAuthorizer",
    "BasicAuthorizer",
    "AccessTokenAuthorizer",
    "RefreshTokenAuthorizer",
    "ClientCredentialsAuthorizer",
    "AuthClient",
    "NativeAppAuthClient",
    "ConfidentialAppAuthClient",
    "OAuthDependentTokenResponse",
    "OAuthTokenResponse",
    "IdentityMap",
    "TransferClient",
    "TransferData",
    "DeleteData",
    "ActivationRequirementsResponse",
    "IterableTransferResponse",
    "SearchClient",
    "SearchQuery",
    "SearchScrollQuery",
    "GroupsClient",
    "BatchMembershipActions",
    "GroupPolicies",
    "GroupMemberVisibility",
    "GroupRequiredSignupFields",
    "GroupRole",
    "GroupVisibility",
    "GroupsManager",
    "GCSClient",
    "GCSRoleDocument",
    "CollectionDocument",
    "GuestCollectionDocument",
    "MappedCollectionDocument",
    "GCSAPIError",
    "GlobusConnectPersonalOwnerInfo",
    "LocalGlobusConnectPersonal",
)


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())

# the warning on imports of `testing` can be disabled via an env var or at runtime
#
# the `testing` module is private, but linters may complain about private imports
# so we use the `testing` name to accommodate linting within the Globus team, but
# guarded with a warning
_DISABLE_TESTING_WARNING = os.getenv("GLOBUS_SDK_DISABLE_TESTING_WARNING") is not None
