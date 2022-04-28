import abc
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from globus_sdk import utils
from globus_sdk.types import UUIDLike

from ._common import ensure_datatype


class StorageGatewayDocument(utils.PayloadWrapper):
    """
    Convenience class for constructing a Storage Gateway document
    to use as the `data` parameter to ``create_storage_gateway`` or
    ``update_storage_gateway``

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param display_name: Name of the Storage Gateway
    :type display_name: str, optional
    :param connector_id: UUID of the connector type that this Storage Gateway interacts
        with.
    :type connector_id: str, optional
    :param identity_mappings: A list of IdentityMapping objects which are applied to
        user identities to attempt to determine what accounts are available for access.
    :type identity_mappings: iterable of dict, optional
    :param policies: Connector specific storage policies. It is recommended that
        you use one of the policy helper classes (e.g. `POSIXStoragePolicies`
        if you are using the POSIX connector) to create these.
    :type policies: dict or StorageGatewayPolicy, optional
    :param allowed_domains: List of allowed domains. Users creating credentials or
        collections on this Storage Gateway must have an identity in one of these
        domains.
    :type allowed_domains: iterable of string
    :param restrict_paths: Path restrictions within this Storage Gateway. Private.
    :type restrict_paths: dict, optional
    :param high_assurance: Flag indicating if the Storage Gateway requires high
        assurance features.
    :type high_assurance: bool, optional
    :param authentication_timeout_mins: Timeout (in minutes) during which a user is
        required to have authenticated in a session to access this storage gateway.
    :type authentication_timeout_mins: int, optional
    :param users_allow:  List of connector-specific usernames allowed to access this
        Storage Gateway. Private.
    :type users_allow: iterable of str, optional
    :param users_deny: List of connector-specific usernames denied access to this
        Storage Gateway. Private.
    :type users_deny: iterable of str, optional
    :param process_user: Local POSIX user the GridFTP server should run as when
        accessing this Storage Gateway.
    :type process_user: str, optional
    :param load_dsi_module: Name of the DSI module to load by the GridFTP server when
        accessing this Storage Gateway.
    :type load_dsi_module: str, optional
    :param require_mfa: Flag indicating that the Storage Gateway requires multi-factor
        authentication. Only usable on high assurance Storage Gateways.
    :type require_mfa: bool, optional

    :param additional_fields: Additional data for inclusion in the Storage Gateway
        document
    :type additional_fields: dict, optional
    """

    DATATYPE_BASE: str = "storage_gateway"
    DATATYPE_VERSION_IMPLICATIONS: Dict[str, Tuple[int, int, int]] = {
        "require_mfa": (1, 1, 0),
    }

    def __init__(
        self,
        DATA_TYPE: Optional[str] = None,
        display_name: Optional[str] = None,
        connector_id: Optional[UUIDLike] = None,
        root: Optional[str] = None,
        identity_mappings: Optional[Iterable[Dict[str, Any]]] = None,
        policies: Union["StorageGatewayPolicies", Dict[str, Any], None] = None,
        allowed_domains: Optional[Iterable[str]] = None,
        high_assurance: Optional[bool] = None,
        require_mfa: Optional[bool] = None,
        authentication_timeout_mins: Optional[int] = None,
        users_allow: Optional[Iterable[str]] = None,
        users_deny: Optional[Iterable[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(
            DATA_TYPE=DATA_TYPE,
            display_name=display_name,
            connector_id=connector_id,
            root=root,
        )
        self._set_optstrlists(
            allow_domains=allowed_domains,
            users_allow=users_allow,
            users_deny=users_deny,
        )
        self._set_optbools(high_assurance=high_assurance, require_mfa=require_mfa)
        self._set_value("identity_mappings", identity_mappings, callback=list)
        self._set_value("policies", policies, callback=dict)
        self._set_value(
            "authentication_timeout_mins", authentication_timeout_mins, callback=int
        )
        if additional_fields is not None:
            self.update(additional_fields)
        ensure_datatype(self)


class StorageGatewayPolicies(utils.PayloadWrapper, abc.ABC):
    """
    This is the abstract base type for Storage Policies documents to use as the
    ``policies`` parameter when creating a StorageGatewayDocument.

    Several fields on policy documents are marked as ``Private``. This means that they
    are not visible except to admins and owners of the storage gateway.
    """


class POSIXStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument

    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :type groups_allow: iterable of str, optional
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :type groups_deny: iterable of str, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_storage_policies#1.0.0",
        groups_allow: Optional[Iterable[str]] = None,
        groups_deny: Optional[Iterable[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE)
        self._set_optstrlists(groups_allow=groups_allow, groups_deny=groups_deny)
        if additional_fields is not None:
            self.update(additional_fields)


class POSIXStagingStoragePolicies(StorageGatewayPolicies):
    """
    Convenience class for constructing a POSIX Staging Storage Policy document
    to use as the ``policies`` parameter when creating a StorageGatewayDocument


    :param DATA_TYPE: Versioned document type. Defaults to the appropriate type for
        this class.
    :type DATA_TYPE: str, optional
    :param groups_allow: List of POSIX group IDs allowed to access this Storage
        Gateway. Private.
    :type groups_allow: iterable of str, optional
    :param groups_deny: List of POSIX group IDs denied access this Storage
        Gateway. Private.
    :type groups_deny: iterable of str, optional
    :param stage_app: Path to the stage app. Private.
    :type stage_app: str, optional
    :param environment: A mapping of variable names to values to set in the environment
        when executing the ``stage_app``. Private.
    :type environment: iterable of dict, optional
    """

    def __init__(
        self,
        DATA_TYPE: str = "posix_staging_storage_policies#1.0.0",
        groups_allow: Optional[Iterable[str]] = None,
        groups_deny: Optional[Iterable[str]] = None,
        stage_app: Optional[str] = None,
        environment: Optional[Iterable[Dict[str, str]]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._set_optstrs(DATA_TYPE=DATA_TYPE, stage_app=stage_app)
        self._set_optstrlists(groups_allow=groups_allow, groups_deny=groups_deny)
        self._set_value(
            "environment",
            environment,
            callback=lambda env_iter: [{**e} for e in env_iter],
        )
        if additional_fields is not None:
            self.update(additional_fields)
