#!/usr/bin/env python
from __future__ import annotations

import itertools
import pathlib
import textwrap
import typing as t

HERE = pathlib.Path(__file__).parent

FIXED_PREAMBLE = f"""\
# isort:skip_file
# fmt:off
#
# this __init__.py file is generated by {pathlib.Path(__file__).name}
# do not edit it directly or testing will fail
import importlib
import logging
import sys
import typing as t

from .version import __version__


def _force_eager_imports() -> None:
    current_module = sys.modules[__name__]

    for attribute_set in _LAZY_IMPORT_TABLE.values():
        for attr in attribute_set:
            getattr(current_module, attr)
"""

FIXED_EPILOG = """
# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_sdk").addHandler(logging.NullHandler())
"""

FIXED_MODULE_METHODS = """\
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
    for modname, items in _LAZY_IMPORT_TABLE.items():
        if name in items:
            mod = importlib.import_module("." + modname, __name__)
            value = getattr(mod, name)
            setattr(sys.modules[__name__], name, value)
            return value

    raise AttributeError(f"module {__name__} has no attribute {name}")
"""


_LAZY_IMPORT_TABLE: list[tuple[str, tuple[str, ...]]] = [
    (
        "authorizers",
        (
            "AccessTokenAuthorizer",
            "BasicAuthorizer",
            "ClientCredentialsAuthorizer",
            "NullAuthorizer",
            "RefreshTokenAuthorizer",
        ),
    ),
    ("client", ("BaseClient",)),
    (
        "exc",
        (
            "GlobusAPIError",
            "ErrorSubdocument",
            "GlobusConnectionError",
            "GlobusConnectionTimeoutError",
            "GlobusError",
            "GlobusSDKUsageError",
            "GlobusTimeoutError",
            "NetworkError",
            "RemovedInV4Warning",
            "ValidationError",
        ),
    ),
    (
        "local_endpoint",
        (
            "GlobusConnectPersonalOwnerInfo",
            "LocalGlobusConnectPersonal",
            "LocalGlobusConnectServer",
        ),
    ),
    (
        "response",
        (
            "GlobusHTTPResponse",
            "IterableResponse",
            "ArrayResponse",
        ),
    ),
    (
        "services.auth",
        (
            # client classes
            "AuthClient",
            "AuthLoginClient",
            "NativeAppAuthClient",
            "ConfidentialAppAuthClient",
            # errors
            "AuthAPIError",
            # high-level helpers
            "IdentityMap",
            "IDTokenDecoder",
            "DefaultIDTokenDecoder",
            # responses
            "GetConsentsResponse",
            "GetIdentitiesResponse",
            "OAuthAuthorizationCodeResponse",
            "OAuthClientCredentialsResponse",
            "OAuthDependentTokenResponse",
            "OAuthRefreshTokenResponse",
            "OAuthTokenResponse",
            # API data helpers
            "DependentScopeSpec",
        ),
    ),
    (
        "services.gcs",
        (
            "CollectionDocument",
            "GCSAPIError",
            "GCSClient",
            "GCSRoleDocument",
            "EndpointDocument",
            "GuestCollectionDocument",
            "MappedCollectionDocument",
            "CollectionPolicies",
            "POSIXCollectionPolicies",
            "POSIXStagingCollectionPolicies",
            "GoogleCloudStorageCollectionPolicies",
            "StorageGatewayDocument",
            "StorageGatewayPolicies",
            "POSIXStoragePolicies",
            "POSIXStagingStoragePolicies",
            "BlackPearlStoragePolicies",
            "BoxStoragePolicies",
            "CephStoragePolicies",
            "GoogleDriveStoragePolicies",
            "GoogleCloudStoragePolicies",
            "OneDriveStoragePolicies",
            "AzureBlobStoragePolicies",
            "S3StoragePolicies",
            "ActiveScaleStoragePolicies",
            "IrodsStoragePolicies",
            "HPSSStoragePolicies",
            "UserCredentialDocument",
            "IterableGCSResponse",
            "UnpackingGCSResponse",
            "GlobusConnectServerConnector",
            "ConnectorTable",
        ),
    ),
    (
        "services.flows",
        (
            "FlowsClient",
            "FlowsAPIError",
            "IterableFlowsResponse",
            "SpecificFlowClient",
        ),
    ),
    (
        "services.groups",
        (
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
    ),
    (
        "services.search",
        (
            "SearchAPIError",
            "SearchClient",
            "SearchQuery",
            "SearchScrollQuery",
        ),
    ),
    (
        "services.timers",
        (
            "TimersAPIError",
            "TimersClient",
            "TransferTimer",
            "TimerJob",
            "OnceTimerSchedule",
            "RecurringTimerSchedule",
        ),
    ),
    (  # legacy module (remove in the future)
        "services.timer",
        (
            "TimerAPIError",
            "TimerClient",
        ),
    ),
    (
        "services.transfer",
        (
            "ActivationRequirementsResponse",
            "DeleteData",
            "IterableTransferResponse",
            "TransferAPIError",
            "TransferClient",
            "TransferData",
        ),
    ),
    (
        "scopes",
        (
            "Scope",
            "ScopeParseError",
            "ScopeCycleError",
        ),
    ),
    (
        "utils",
        (
            "MISSING",
            "MissingType",
        ),
    ),
]


def _generate_imports() -> t.Iterator[str]:
    for modname, items in _LAZY_IMPORT_TABLE:
        for item in items:
            yield textwrap.indent(f"from .{modname} import {item}", "    ")


def _generate_lazy_import_table() -> t.Iterator[str]:
    yield "_LAZY_IMPORT_TABLE = {"
    for modname, items in _LAZY_IMPORT_TABLE:
        yield textwrap.indent(f'"{modname}": {{', " " * 4)
        for item in items:
            yield textwrap.indent(f'"{item}",', " " * 8)
        yield textwrap.indent("},", " " * 4)
    yield "}"


def _generate_all_tuple() -> t.Iterator[str]:
    yield "__all__ = ("
    yield '    "__version__",'
    yield '    "_force_eager_imports",'
    yield from (
        f'    "{item}",'
        for item in sorted(itertools.chain(*[items for _, items in _LAZY_IMPORT_TABLE]))
    )
    yield ")"


def _init_pieces() -> t.Iterator[str]:
    yield FIXED_PREAMBLE
    yield ""
    yield from _generate_lazy_import_table()
    yield ""
    yield "if t.TYPE_CHECKING:"
    yield from _generate_imports()
    yield ""
    yield "else:"
    yield ""
    yield textwrap.indent(FIXED_MODULE_METHODS, "    ")
    yield ""
    yield from _generate_all_tuple()
    yield ""
    yield FIXED_EPILOG


def _generate_init() -> str:
    return "\n".join(_init_pieces())


def main() -> None:
    with open(HERE / "__init__.py", "w", encoding="utf-8") as fp:
        fp.write(_generate_init())


if __name__ == "__main__":
    main()
