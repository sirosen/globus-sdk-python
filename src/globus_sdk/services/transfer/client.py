import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Union

from globus_sdk import client, exc, paging, response, utils
from globus_sdk.scopes import TransferScopes
from globus_sdk.types import UUIDLike

from .data import DeleteData, TransferData
from .errors import TransferAPIError
from .response import ActivationRequirementsResponse, IterableTransferResponse

log = logging.getLogger(__name__)


def _get_page_size(paged_result: IterableTransferResponse) -> int:
    return len(paged_result["DATA"])


class TransferClient(client.BaseClient):
    r"""
    Client for the
    `Globus Transfer API <https://docs.globus.org/api/transfer/>`_.

    This class provides helper methods for most common resources in the
    REST API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base rest client that can be used to access any REST resource.

    Detailed documentation is available in the official REST API
    documentation, which is linked to from the method documentation. Methods
    that allow arbitrary keyword arguments will pass the extra arguments as
    query parameters.

    :param authorizer: An authorizer instance used for all calls to
                       Globus Transfer
    :type authorizer: :class:`GlobusAuthorizer\
                      <globus_sdk.authorizers.base.GlobusAuthorizer>`

    **Paginated Calls**

    Methods which support pagination can be called as paginated or unpaginated methods.
    If the method name is ``TransferClient.foo``, the paginated version is
    ``TransferClient.paginated.foo``.
    Using ``TransferClient.endpoint_search`` as an example::

        from globus_sdk import TransferClient
        tc = TransferClient(...)

        # this is the unpaginated version
        for x in tc.endpoint_search("tutorial"):
            print("Endpoint ID: {}".format(x["id"]))

        # this is the paginated version
        for page in tc.paginated.endpoint_search("testdata"):
            for x in page:
                print("Endpoint ID: {}".format(x["id"]))

    .. automethodlist:: globus_sdk.TransferClient
    """
    service_name = "transfer"
    base_path = "/v0.10/"
    error_class = TransferAPIError
    scopes = TransferScopes

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

    @utils.doc_api_method("Get Endpoint by ID", "transfer/endpoint/#get_endpoint_by_id")
    def get_endpoint(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> endpoint = tc.get_endpoint(endpoint_id)
        >>> print("Endpoint name:",
        >>>       endpoint["display_name"] or endpoint["canonical_name"])
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.get_endpoint({endpoint_id})")
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Update Endpoint by ID", "transfer/endpoint/#update_endpoint_by_id"
    )
    def update_endpoint(
        self,
        endpoint_id: UUIDLike,
        data: dict,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> epup = dict(display_name="My New Endpoint Name",
        >>>             description="Better Description")
        >>> update_result = tc.update_endpoint(endpoint_id, epup)
        """
        if data.get("myproxy_server"):
            if data.get("oauth_server"):
                raise exc.GlobusSDKUsageError(
                    "an endpoint cannot be reconfigured to use multiple "
                    "identity providers for activation; specify either "
                    "MyProxy or OAuth, not both"
                )
            else:
                data["oauth_server"] = None
        elif data.get("oauth_server"):
            data["myproxy_server"] = None

        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.update_endpoint({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.put(path, data=data, query_params=query_params)

    @utils.doc_api_method("Create Endpoint", "transfer/endpoint/#create_endpoint")
    def create_endpoint(self, data: dict) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> ep_data = {
        >>>   "DATA_TYPE": "endpoint",
        >>>   "display_name": display_name,
        >>>   "DATA": [
        >>>     {
        >>>       "DATA_TYPE": "server",
        >>>       "hostname": "gridftp.example.edu",
        >>>     },
        >>>   ],
        >>> }
        >>> create_result = tc.create_endpoint(ep_data)
        >>> endpoint_id = create_result["id"]
        """
        if data.get("myproxy_server") and data.get("oauth_server"):
            raise exc.GlobusSDKUsageError(
                "an endpoint cannot be created using multiple identity "
                "providers for activation; specify either MyProxy or OAuth, "
                "not both"
            )

        log.info("TransferClient.create_endpoint(...)")
        return self.post("endpoint", data=data)

    @utils.doc_api_method(
        "Delete Endpoint by ID", "transfer/endpoint/#delete_endpoint_by_id"
    )
    def delete_endpoint(self, endpoint_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> delete_result = tc.delete_endpoint(endpoint_id)
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.delete_endpoint({endpoint_id})")
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.delete(path)

    @utils.doc_api_method("Endpoint Search", "transfer/endpoint_search")
    @paging.has_paginator(
        paging.HasNextPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=100,
    )
    def endpoint_search(
        self,
        filter_fulltext: Optional[str] = None,
        filter_scope: Optional[str] = None,
        filter_owner_id: Optional[str] = None,
        filter_host_endpoint: Optional[UUIDLike] = None,
        filter_non_functional: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        r"""
        .. parsed-literal::

            GET /endpoint_search\
            ?filter_fulltext=<filter_fulltext>&filter_scope=<filter_scope>

        :param filter_fulltext: The string to use in a full text search on endpoints.
            Effectively, the "search query" which is being requested. May be omitted
            with specific ``filter_scope`` values.
        :type filter_fulltext: str, optional
        :param filter_scope: A "scope" within which to search for endpoints. This must
            be one of the limited and known names known to the service, which can be
            found documented in the **External Documentation** below. Defaults to
            searching all endpoints (in which case ``filter_fulltext`` is required)
        :type filter_scope: str, optional
        :param filter_owner_id: Limit search to endpoints owned by the specified Globus
            Auth identity. Conflicts with scopes 'my-endpoints', 'my-gcp-endpoints', and
            'shared-by-me'.
        :type filter_owner_id: str, optional
        :param filter_host_endpoint: Limit search to endpoints hosted by the specified
            endpoint. May cause BadRequest or PermissionDenied errors if the endpoint ID
            given is not valid for this operation.
        :type filter_host_endpoint: str, optional
        :param filter_non_functional: Limit search to endpoints which have the
            'non_functional' flag set to True or False.
        :type filter_non_functional: bool, optional
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Examples**

        Search for a given string as a fulltext search:

        >>> tc = globus_sdk.TransferClient(...)
        >>> for ep in tc.endpoint_search('String to search for!'):
        >>>     print(ep['display_name'])

        Search for a given string, but only on endpoints that you own:

        >>> for ep in tc.endpoint_search('foo', filter_scope='my-endpoints'):
        >>>     print('{0} has ID {1}'.format(ep['display_name'], ep['id']))

        It is important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query.
        """
        if query_params is None:
            query_params = {}
        if filter_scope is not None:
            query_params["filter_scope"] = filter_scope
        if filter_fulltext is not None:
            query_params["filter_fulltext"] = filter_fulltext
        if filter_owner_id is not None:
            query_params["filter_owner_id"] = filter_owner_id
        if filter_host_endpoint is not None:  # convert to str (may be UUID)
            query_params["filter_host_endpoint"] = utils.safe_stringify(
                filter_host_endpoint
            )
        if filter_non_functional is not None:  # convert to int (expect bool input)
            query_params["filter_non_functional"] = 1 if filter_non_functional else 0
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        log.info(f"TransferClient.endpoint_search({query_params})")
        return IterableTransferResponse(
            self.get("endpoint_search", query_params=query_params)
        )

    @utils.doc_api_method(
        "Autoactivate Endpoint", "transfer/endpoint_activation/#autoactivate_endpoint"
    )
    def endpoint_autoactivate(
        self,
        endpoint_id: UUIDLike,
        if_expires_in: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        r"""
        ``POST /endpoint/<endpoint_id>/autoactivate``

        The following example will try to "auto" activate the endpoint
        using a credential available from another endpoint or sign in by
        the user with the same identity provider, but only if the
        endpoint is not already activated or going to expire within an
        hour (3600 seconds). If that fails, direct the user to the
        globus website to perform activation:

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
        >>> while (r["code"] == "AutoActivationFailed"):
        >>>     print("Endpoint requires manual activation, please open "
        >>>           "the following URL in a browser to activate the "
        >>>           "endpoint:")
        >>>     print("https://app.globus.org/file-manager?origin_id=%s"
        >>>           % ep_id)
        >>>     input("Press ENTER after activating the endpoint:")
        >>>     r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)

        This is the recommended flow for most thick client applications,
        because many endpoints require activation via OAuth MyProxy,
        which must be done in a browser anyway. Web based clients can
        link directly to the URL.

        You also might want messaging or logging depending on why and how the
        operation succeeded, in which case you'll need to look at the value of
        the "code" field and either decide on your own messaging or use the
        response's "message" field.

        >>> tc = globus_sdk.TransferClient(...)
        >>> r = tc.endpoint_autoactivate(ep_id, if_expires_in=3600)
        >>> if r['code'] == 'AutoActivationFailed':
        >>>     print('Endpoint({}) Not Active! Error! Source message: {}'
        >>>           .format(ep_id, r['message']))
        >>>     sys.exit(1)
        >>> elif r['code'] == 'AutoActivated.CachedCredential':
        >>>     print('Endpoint({}) autoactivated using a cached credential.'
        >>>           .format(ep_id))
        >>> elif r['code'] == 'AutoActivated.GlobusOnlineCredential':
        >>>     print(('Endpoint({}) autoactivated using a built-in Globus '
        >>>            'credential.').format(ep_id))
        >>> elif r['code'] = 'AlreadyActivated':
        >>>     print('Endpoint({}) already active until at least {}'
        >>>           .format(ep_id, 3600))
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        if query_params is None:
            query_params = {}
        if if_expires_in is not None:
            query_params["if_expires_in"] = if_expires_in
        log.info(f"TransferClient.endpoint_autoactivate({endpoint_id})")
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, query_params=query_params)

    @utils.doc_api_method(
        "Deactive Endpoint", "transfer/endpoint_activation/#deactivate_endpoint"
    )
    def endpoint_deactivate(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/deactivate``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_deactivate({endpoint_id})")
        path = self.qjoin_path("endpoint", endpoint_id, "deactivate")
        return self.post(path, query_params=query_params)

    @utils.doc_api_method(
        "Activate Endpoint", "transfer/endpoint_activation/#activate_endpoint"
    )
    def endpoint_activate(
        self,
        endpoint_id: UUIDLike,
        requirements_data: Optional[dict],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/activate``

        Consider using autoactivate and web activation instead, described
        in the example for :meth:`~endpoint_autoactivate`.
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_activate({endpoint_id})")
        path = self.qjoin_path("endpoint", endpoint_id, "activate")
        return self.post(path, data=requirements_data, query_params=query_params)

    @utils.doc_api_method(
        "Get Activation Requirements",
        "transfer/endpoint_activation/#get_activation_requirements",
    )
    def endpoint_get_activation_requirements(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> ActivationRequirementsResponse:
        """
        ``GET /endpoint/<endpoint_id>/activation_requirements``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        path = self.qjoin_path("endpoint", endpoint_id, "activation_requirements")
        return ActivationRequirementsResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get my effective endpoint pause rules",
        "transfer/endpoint/#get_endpoint_pause_rules",
    )
    def my_effective_pause_rule_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/my_effective_pause_rule_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.my_effective_pause_rule_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "my_effective_pause_rule_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    # Shared Endpoints

    @utils.doc_api_method(
        "Get shared endpoint list", "transfer/endpoint/#get_shared_endpoint_list"
    )
    def my_shared_endpoint_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/my_shared_endpoint_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.my_shared_endpoint_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "my_shared_endpoint_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get shared endpoint list (2)", "transfer/endpoint/#get_shared_endpoint_list2"
    )
    @paging.has_paginator(
        paging.NextTokenPaginator,
        items_key="shared_endpoints",
    )
    def get_shared_endpoint_list(
        self,
        endpoint_id: UUIDLike,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/shared_endpoint_list``

        :param max_results: cap to the number of results
        :type max_results: int, optional
        :param next_token: token used for paging
        :type next_token: str, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_param: dict, optional
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.get_shared_endpoint_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "shared_endpoint_list")
        if query_params is None:
            query_params = {}
        if max_results is not None:
            query_params["max_results"] = str(max_results)
        if next_token is not None:
            query_params["next_token"] = str(next_token)
        return IterableTransferResponse(
            self.get(path, query_params=query_params), iter_key="shared_endpoints"
        )

    @utils.doc_api_method(
        "Create Shared Endpoint", "transfer/endpoint/#create_shared_endpoint"
    )
    def create_shared_endpoint(
        self, data: Optional[dict]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /shared_endpoint``

        :param data: A python dict representation of a ``shared_endpoint`` document
        :type data: dict

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> shared_ep_data = {
        >>>   "DATA_TYPE": "shared_endpoint",
        >>>   "host_endpoint": host_endpoint_id,
        >>>   "host_path": host_path,
        >>>   "display_name": display_name,
        >>>   # optionally specify additional endpoint fields
        >>>   "description": "my test share"
        >>> }
        >>> create_result = tc.create_shared_endpoint(shared_ep_data)
        >>> endpoint_id = create_result["id"]
        """
        log.info("TransferClient.create_shared_endpoint(...)")
        return self.post("shared_endpoint", data=data)

    # Endpoint servers

    @utils.doc_api_method(
        "Get endpoint server list", "transfer/endpoint/#get_endpoint_server_list"
    )
    def endpoint_server_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/server_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_server_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "server_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get endpoint server by id", "transfer/endpoint/#get_endpoint_server_by_id"
    )
    def get_endpoint_server(
        self,
        endpoint_id: UUIDLike,
        server_id: UUIDLike,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/server/<server_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.get_endpoint_server(%s, %s, ...)", endpoint_id, server_id
        )
        path = self.qjoin_path("endpoint", endpoint_id, "server", str(server_id))
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Add endpoint server", "transfer/endpoint/#add_endpoint_server"
    )
    def add_endpoint_server(
        self, endpoint_id: UUIDLike, server_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/server``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_server({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "server")
        return self.post(path, data=server_data)

    @utils.doc_api_method(
        "Update endpoint server by ID",
        "transfer/endpoint/#update_endpoint_server_by_id",
    )
    def update_endpoint_server(
        self, endpoint_id: UUIDLike, server_id: UUIDLike, server_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>/server/<server_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.update_endpoint_server(%s, %s, ...)",
            endpoint_id,
            server_id,
        )
        path = self.qjoin_path("endpoint", endpoint_id, "server", str(server_id))
        return self.put(path, data=server_data)

    @utils.doc_api_method(
        "Delete endpoint server by ID",
        "transfer/endpoint/#delete_endpoint_server_by_id",
    )
    def delete_endpoint_server(
        self, endpoint_id: UUIDLike, server_id: UUIDLike
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/server/<server_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.delete_endpoint_server(%s, %s)", endpoint_id, server_id
        )
        path = self.qjoin_path("endpoint", endpoint_id, "server", str(server_id))
        return self.delete(path)

    #
    # Roles
    #

    @utils.doc_api_method(
        "Get list of endpoint roles", "transfer/endpoint_roles/#role_list"
    )
    def endpoint_role_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/role_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_role_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "role_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Create endpoint role", "transfer/endpoint_roles/#create_role"
    )
    def add_endpoint_role(
        self, endpoint_id: UUIDLike, role_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/role``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_role({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "role")
        return self.post(path, data=role_data)

    @utils.doc_api_method(
        "Get endpoint role by ID", "transfer/endpoint_roles/#get_endpoint_role_by_id"
    )
    def get_endpoint_role(
        self,
        endpoint_id: UUIDLike,
        role_id: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/role/<role_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.get_endpoint_role({endpoint_id}, {role_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "role", role_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Delete endpoint role by ID",
        "transfer/endpoint_roles/#delete_endpoint_role_by_id",
    )
    def delete_endpoint_role(
        self, endpoint_id: UUIDLike, role_id: str
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/role/<role_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.delete_endpoint_role({endpoint_id}, {role_id})")
        path = self.qjoin_path("endpoint", endpoint_id, "role", role_id)
        return self.delete(path)

    #
    # ACLs
    #

    @utils.doc_api_method(
        "Get list of access rules", "transfer/acl/#rest_access_get_list"
    )
    def endpoint_acl_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /endpoint/<endpoint_id>/access_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_acl_list({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "access_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get access rule by ID", "transfer/acl/#get_access_rule_by_id"
    )
    def get_endpoint_acl_rule(
        self,
        endpoint_id: UUIDLike,
        rule_id: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /endpoint/<endpoint_id>/access/<rule_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.get_endpoint_acl_rule(%s, %s, ...)", endpoint_id, rule_id
        )
        path = self.qjoin_path("endpoint", endpoint_id, "access", rule_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method("Create access rule", "transfer/acl/#rest_access_create")
    def add_endpoint_acl_rule(
        self, endpoint_id: UUIDLike, rule_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /endpoint/<endpoint_id>/access``

        :param endpoint_id: ID of endpoint to which to add the acl
        :type endpoint_id: str
        :param rule_data: A python dict representation of an ``access`` document
        :type rule_data: dict

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "DATA_TYPE": "access",
        >>>   "principal_type": "identity",
        >>>   "principal": identity_id,
        >>>   "path": "/dataset1/",
        >>>   "permissions": "rw",
        >>> }
        >>> result = tc.add_endpoint_acl_rule(endpoint_id, rule_data)
        >>> rule_id = result["access_id"]

        Note that if this rule is being created on a shared endpoint
        the "path" field is relative to the "host_path" of the shared endpoint.
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.add_endpoint_acl_rule({endpoint_id}, ...)")
        path = self.qjoin_path("endpoint", endpoint_id, "access")
        return self.post(path, data=rule_data)

    @utils.doc_api_method("Update access rule", "transfer/acl/#update_access_rule")
    def update_endpoint_acl_rule(
        self, endpoint_id: UUIDLike, rule_id: str, rule_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /endpoint/<endpoint_id>/access/<rule_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.update_endpoint_acl_rule(%s, %s, ...)",
            endpoint_id,
            rule_id,
        )
        path = self.qjoin_path("endpoint", endpoint_id, "access", rule_id)
        return self.put(path, data=rule_data)

    @utils.doc_api_method("Delete access rule", "transfer/acl/#delete_access_rule")
    def delete_endpoint_acl_rule(
        self, endpoint_id: UUIDLike, rule_id: str
    ) -> response.GlobusHTTPResponse:
        """
        ``DELETE /endpoint/<endpoint_id>/access/<rule_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.delete_endpoint_acl_rule(%s, %s)", endpoint_id, rule_id
        )
        path = self.qjoin_path("endpoint", endpoint_id, "access", rule_id)
        return self.delete(path)

    #
    # Bookmarks
    #

    @utils.doc_api_method(
        "Get list of bookmarks", "transfer/endpoint_bookmarks/#get_list_of_bookmarks"
    )
    def bookmark_list(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        ``GET /bookmark_list``
        """
        log.info(f"TransferClient.bookmark_list({query_params})")
        return IterableTransferResponse(
            self.get("bookmark_list", query_params=query_params)
        )

    @utils.doc_api_method(
        "Create bookmark", "transfer/endpoint_bookmarks/#create_bookmark"
    )
    def create_bookmark(self, bookmark_data: Dict) -> response.GlobusHTTPResponse:
        """
        ``POST /bookmark``
        """
        log.info(f"TransferClient.create_bookmark({bookmark_data})")
        return self.post("bookmark", data=bookmark_data)

    @utils.doc_api_method(
        "Get bookmark by ID", "transfer/endpoint_bookmarks/#get_bookmark_by_id"
    )
    def get_bookmark(
        self, bookmark_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /bookmark/<bookmark_id>``
        """
        bookmark_id = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.get_bookmark({bookmark_id})")
        path = self.qjoin_path("bookmark", bookmark_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Update bookmark", "transfer/endpoint_bookmarks/#update_bookmark"
    )
    def update_bookmark(
        self, bookmark_id: UUIDLike, bookmark_data: Dict
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /bookmark/<bookmark_id>``
        """
        bookmark_id = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.update_bookmark({bookmark_id})")
        path = self.qjoin_path("bookmark", bookmark_id)
        return self.put(path, data=bookmark_data)

    @utils.doc_api_method(
        "Delete bookmark by ID", "transfer/endpoint_bookmarks/#delete_bookmark_by_id"
    )
    def delete_bookmark(self, bookmark_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        ``DELETE /bookmark/<bookmark_id>``
        """
        bookmark_id = utils.safe_stringify(bookmark_id)
        log.info(f"TransferClient.delete_bookmark({bookmark_id})")
        path = self.qjoin_path("bookmark", bookmark_id)
        return self.delete(path)

    #
    # Synchronous Filesys Operations
    #

    @utils.doc_api_method(
        "List Directory Contents", "transfer/file_operations/#list_directory_contents"
    )
    def operation_ls(
        self,
        endpoint_id: UUIDLike,
        path: Optional[str] = None,
        show_hidden: Optional[bool] = None,
        orderby: Optional[Union[str, List[str]]] = None,
        # note: filter is a soft keyword in python, so using this name is okay
        filter: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        """
        ``GET /operation/endpoint/<endpoint_id>/ls``

        :param path: Path to a directory on the endpoint to list
        :type path: str, optional
        :param show_hidden: Show hidden files (names beginning in dot).
            Defaults to true.
        :type show_hidden: bool, optional
        :param orderby: One or more order-by options. Each option is
            either a field name or a field name followed by a space and 'ASC' or 'DESC'
            for ascending or descending.
        :type orderby: str, optional
        :param filter: Only return file documents that match these filter clauses. For
            the filter syntax, see the **External Documentation** linked below.
        :type filter: str, optional

        **Examples**

        List with a path:

        >>> tc = globus_sdk.TransferClient(...)
        >>> for entry in tc.operation_ls(ep_id, path="/~/project1/"):
        >>>     print(entry["name"], entry["type"])

        List with explicit ordering:

        >>> tc = globus_sdk.TransferClient(...)
        >>> for entry in tc.operation_ls(
        >>>     ep_id,
        >>>     path="/~/project1/",
        >>>     orderby=["type", "name"]
        >>> ):
        >>>     print(entry["name DESC"], entry["type"])
        """
        endpoint_id = utils.safe_stringify(endpoint_id)

        if query_params is None:
            query_params = {}
        if path is not None:
            query_params["path"] = path
        if show_hidden is not None:
            query_params["show_hidden"] = 1 if show_hidden else 0
        if orderby is not None:
            if isinstance(orderby, str):
                query_params["orderby"] = orderby
            else:
                query_params["orderby"] = ",".join(orderby)
        if filter is not None:
            query_params["filter"] = filter

        log.info(f"TransferClient.operation_ls({endpoint_id}, {query_params})")
        req_path = self.qjoin_path("operation/endpoint", endpoint_id, "ls")
        return IterableTransferResponse(self.get(req_path, query_params=query_params))

    @utils.doc_api_method("Make Directory", "transfer/file_operations/#make_directory")
    def operation_mkdir(
        self,
        endpoint_id: UUIDLike,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/mkdir``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_mkdir(ep_id, path="/~/newdir/")
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        path = utils.safe_stringify(path)
        log.info(
            "TransferClient.operation_mkdir({}, {}, {})".format(
                endpoint_id, path, query_params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id, "mkdir")
        json_body = {"DATA_TYPE": "mkdir", "path": path}
        return self.post(resource_path, data=json_body, query_params=query_params)

    @utils.doc_api_method("Rename", "transfer/file_operations/#rename")
    def operation_rename(
        self,
        endpoint_id: UUIDLike,
        oldpath: str,
        newpath: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/rename``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_rename(ep_id, oldpath="/~/file1.txt",
        >>>                     newpath="/~/project1data.txt")
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.operation_rename({}, {}, {}, {})".format(
                endpoint_id, oldpath, newpath, query_params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id, "rename")
        json_body = {"DATA_TYPE": "rename", "old_path": oldpath, "new_path": newpath}
        return self.post(resource_path, data=json_body, query_params=query_params)

    @utils.doc_api_method("Symlink", "transfer/file_operations/#symlink")
    def operation_symlink(
        self,
        endpoint_id: UUIDLike,
        symlink_target: str,
        path: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /operation/endpoint/<endpoint_id>/symlink``

        The ``path`` is the name of the symlink, and the ``symlink_target`` is
        the path referenced by the symlink.

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tc.operation_symlink(ep_id, symlink_target="/~/file1.txt",
        >>>                      path="/~/link-to-file1.txt")
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            "TransferClient.operation_symlink({}, {}, {}, {})".format(
                endpoint_id, symlink_target, path, query_params
            )
        )
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id, "symlink")
        data = {
            "DATA_TYPE": "symlink",
            "symlink_target": symlink_target,
            "path": path,
        }
        return self.post(resource_path, data=data, query_params=query_params)

    #
    # Task Submission
    #

    @utils.doc_api_method(
        "Get a submission ID", "transfer/task_submit/#get_submission_id"
    )
    def get_submission_id(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /submission_id``

        Submission IDs are required to submit tasks to the Transfer service
        via the :meth:`submit_transfer <.submit_transfer>` and
        :meth:`submit_delete <.submit_delete>` methods.

        Most users will not need to call this method directly, as the
        convenience classes :class:`TransferData <globus_sdk.TransferData>`
        and :class:`DeleteData <globus_sdk.DeleteData>` will call it
        automatically if they are not passed a ``submission_id`` explicitly.
        """
        log.info(f"TransferClient.get_submission_id({query_params})")
        return self.get("submission_id", query_params=query_params)

    @utils.doc_api_method(
        "Submit a transfer task", "transfer/task_submit/#submit_transfer_task"
    )
    def submit_transfer(
        self, data: Union[Dict[str, Any], TransferData]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /transfer``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> tdata = globus_sdk.TransferData(tc, source_endpoint_id,
        >>>                                 destination_endpoint_id,
        >>>                                 label="SDK example",
        >>>                                 sync_level="checksum")
        >>> tdata.add_item("/source/path/dir/", "/dest/path/dir/",
        >>>                recursive=True)
        >>> tdata.add_item("/source/path/file.txt",
        >>>                "/dest/path/file.txt")
        >>> transfer_result = tc.submit_transfer(tdata)
        >>> print("task_id =", transfer_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`TransferData <globus_sdk.TransferData>` object.
        """
        log.info("TransferClient.submit_transfer(...)")
        return self.post("/transfer", data=data)

    @utils.doc_api_method(
        "Submit a delete task", "transfer/task_submit/#submit_delete_task"
    )
    def submit_delete(
        self, data: Union[Dict[str, Any], DeleteData]
    ) -> response.GlobusHTTPResponse:
        """
        ``POST /delete``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> ddata = globus_sdk.DeleteData(tc, endpoint_id, recursive=True)
        >>> ddata.add_item("/dir/to/delete/")
        >>> ddata.add_item("/file/to/delete/file.txt")
        >>> delete_result = tc.submit_delete(ddata)
        >>> print("task_id =", delete_result["task_id"])

        The `data` parameter can be a normal Python dictionary, or
        a :class:`DeleteData <globus_sdk.DeleteData>` object.
        """
        log.info("TransferClient.submit_delete(...)")
        return self.post("/delete", data=data)

    #
    # Task inspection and management
    #

    @utils.doc_api_method("Task list", "transfer/task/#get_task_list")
    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def task_list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        """
        Get an iterable of task documents owned by the current user.

        ``GET /task_list``

        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Examples**

        Fetch 10 tasks and print some basic info:

        >>> tc = TransferClient(...)
        >>> for task in tc.task_list(limit=10):
        >>>     print("Task({}): {} -> {}".format(
        >>>         task["task_id"], task["source_endpoint"],
        >>>         task["destination_endpoint"]))
        """
        log.info("TransferClient.task_list(...)")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        return IterableTransferResponse(
            self.get("task_list", query_params=query_params)
        )

    @utils.doc_api_method("Get event list", "transfer/task/#get_event_list")
    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def task_event_list(
        self,
        task_id: UUIDLike,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        r"""
        List events (for example, faults and errors) for a given Task.

        ``GET /task/<task_id>/event_list``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :type offset: int, optional
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Examples**

        Fetch 10 events and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for event in tc.task_event_list(task_id, limit=10):
        >>>     print("Event on Task({}) at {}:\n{}".format(
        >>>         task_id, event["time"], event["description"])
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_event_list({task_id}, ...)")
        path = self.qjoin_path("task", task_id, "event_list")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method("Get task by ID", "transfer/task/#get_task_by_id")
    def get_task(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /task/<task_id>``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.get_task({task_id}, ...)")
        resource_path = self.qjoin_path("task", task_id)
        return self.get(resource_path, query_params=query_params)

    @utils.doc_api_method("Update task by ID", "transfer/task/#update_task_by_id")
    def update_task(
        self,
        task_id: UUIDLike,
        data: Dict,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        ``PUT /task/<task_id>``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.update_task({task_id}, ...)")
        resource_path = self.qjoin_path("task", task_id)
        return self.put(resource_path, data=data, query_params=query_params)

    @utils.doc_api_method("Cancel task by ID", "transfer/task/#cancel_task_by_id")
    def cancel_task(self, task_id: UUIDLike) -> response.GlobusHTTPResponse:
        """
        ``POST /task/<task_id>/cancel``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.cancel_task({task_id})")
        resource_path = self.qjoin_path("task", task_id, "cancel")
        return self.post(resource_path)

    def task_wait(
        self, task_id: UUIDLike, timeout: int = 10, polling_interval: int = 10
    ) -> bool:
        r"""
        Wait until a Task is complete or fails, with a time limit. If the task
        is "ACTIVE" after time runs out, returns ``False``. Otherwise returns
        ``True``.

        :param task_id: ID of the Task to wait on for completion
        :type task_id: str
        :param timeout: Number of seconds to wait in total. Minimum 1. [Default: ``10``]
        :type timeout: int, optional
        :param polling_interval: Number of seconds between queries to Globus about the
            Task status. Minimum 1. [Default: ``10``]
        :type polling_interval: int, optional

        **Examples**

        If you want to wait for a task to terminate, but want to warn every
        minute that it doesn't terminate, you could:

        >>> tc = TransferClient(...)
        >>> while not tc.task_wait(task_id, timeout=60):
        >>>     print("Another minute went by without {0} terminating"
        >>>           .format(task_id))

        Or perhaps you want to check on a task every minute for 10 minutes, and
        give up if it doesn't complete in that time:

        >>> tc = TransferClient(...)
        >>> done = tc.task_wait(task_id, timeout=600, polling_interval=60):
        >>> if not done:
        >>>     print("{0} didn't successfully terminate!"
        >>>           .format(task_id))
        >>> else:
        >>>     print("{0} completed".format(task_id))

        You could print dots while you wait for a task by only waiting one
        second at a time:

        >>> tc = TransferClient(...)
        >>> while not tc.task_wait(task_id, timeout=1, polling_interval=1):
        >>>     print(".", end="")
        >>> print("\n{0} completed!".format(task_id))
        """
        task_id = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.task_wait({}, {}, {})".format(
                task_id, timeout, polling_interval
            )
        )

        # check valid args
        if timeout < 1:
            log.error(f"task_wait() timeout={timeout} is less than minimum of 1s")
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait timeout has a minimum of 1"
            )
        if polling_interval < 1:
            log.error(
                "task_wait() polling_interval={} is less than minimum of 1s".format(
                    polling_interval
                )
            )
            raise exc.GlobusSDKUsageError(
                "TransferClient.task_wait polling_interval has a minimum of 1"
            )

        # ensure that we always wait at least one interval, even if the timeout
        # is shorter than the polling interval, by reducing the interval to the
        # timeout if it is larger
        polling_interval = min(timeout, polling_interval)

        # helper for readability
        def timed_out(waited_time: int) -> bool:
            return waited_time > timeout

        waited_time = 0
        # doing this as a while-True loop actually makes it simpler than doing
        # while not timed_out(waited_time) because of the end condition
        while True:
            # get task, check if status != ACTIVE
            task = self.get_task(task_id)
            status = task["status"]
            if status != "ACTIVE":
                log.debug(
                    "task_wait(task_id={}) terminated with status={}".format(
                        task_id, status
                    )
                )
                return True

            # make sure to check if we timed out before sleeping again, so we
            # don't sleep an extra polling_interval
            waited_time += polling_interval
            if timed_out(waited_time):
                log.debug(f"task_wait(task_id={task_id}) timed out")
                return False

            log.debug(f"task_wait(task_id={task_id}) waiting {polling_interval}s")
            time.sleep(polling_interval)
        # unreachable -- end of task_wait

    @utils.doc_api_method("Get task pause info", "transfer/task/#get_task_pause_info")
    def task_pause_info(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        ``GET /task/<task_id>/pause_info``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_pause_info({task_id}, ...)")
        resource_path = self.qjoin_path("task", task_id, "pause_info")
        return self.get(resource_path, query_params=query_params)

    @utils.doc_api_method(
        "Get Task Successful Transfer", "transfer/task/#get_task_successful_transfers"
    )
    @paging.has_paginator(paging.MarkerPaginator, items_key="DATA")
    def task_successful_transfers(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get the successful file transfers for a completed Task.

        .. note::

            Only files that were actually transferred are included. This does
            not include directories, files that were checked but skipped as
            part of a sync transfer, or files which were skipped due to
            skip_source_errors being set on the task.

        ``GET /task/<task_id>/successful_transfers``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Examples**

        Fetch all transferred files for a task and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for info in tc.task_successful_transfers(task_id):
        >>>     print("{} -> {}".format(
        >>>         info["source_path"], info["destination_path"]))
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.task_successful_transfers({task_id}, ...)")
        path = self.qjoin_path("task", task_id, "successful_transfers")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get Task Skipped Errors", "transfer/task/#get_task_skipped_errors"
    )
    @paging.has_paginator(paging.MarkerPaginator, items_key="DATA")
    def task_skipped_errors(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get path and error information for all paths that were skipped due
        to skip_source_errors being set on a completed transfer Task.

        ``GET /task/<task_id>/skipped_errors``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Examples**

        Fetch all skipped errors for a task and print some basic info:

        >>> tc = TransferClient(...)
        >>> task_id = ...
        >>> for info in tc.task_skipped_errors(task_id):
        >>>     print("{} -> {}".format(
        >>>         info["error_code"], info["source_path"]))
        """
        task_id = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.endpoint_manager_task_skipped_errors(%s, ...)", task_id
        )
        resource_path = self.qjoin_path("task", task_id, "skipped_errors")
        return IterableTransferResponse(
            self.get(resource_path, query_params=query_params)
        )

    #
    # advanced endpoint management (requires endpoint manager role)
    #

    @utils.doc_api_method(
        "Get monitored endpoints",
        "transfer/advanced_endpoint_management/#get_monitored_endpoints",
    )
    def endpoint_manager_monitored_endpoints(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get endpoints the current user is a monitor or manager on.

        ``GET endpoint_manager/monitored_endpoints``
        """
        log.info(f"TransferClient.endpoint_manager_monitored_endpoints({query_params})")
        path = self.qjoin_path("endpoint_manager", "monitored_endpoints")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get hosted endpoint list",
        "transfer/advanced_endpoint_management/#get_hosted_endpoint_list",
    )
    def endpoint_manager_hosted_endpoint_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get shared endpoints hosted on the given endpoint.

        ``GET /endpoint_manager/endpoint/<endpoint_id>/hosted_endpoint_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_manager_hosted_endpoint_list({endpoint_id})")
        path = self.qjoin_path(
            "endpoint_manager", "endpoint", endpoint_id, "hosted_endpoint_list"
        )
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get endpoint as admin",
        "transfer/advanced_endpoint_management/#mc_get_endpoint",
    )
    def endpoint_manager_get_endpoint(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Get endpoint details as an admin.

        ``GET /endpoint_manager/endpoint/<endpoint_id>``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(f"TransferClient.endpoint_manager_get_endpoint({endpoint_id})")
        path = self.qjoin_path("endpoint_manager", "endpoint", endpoint_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Get endpoint access list as admin",
        "transfer/advanced_endpoint_management/#get_endpoint_access_list_as_admin",
    )
    def endpoint_manager_acl_list(
        self, endpoint_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get a list of access control rules on specified endpoint as an admin.

        ``GET endpoint_manager/endpoint/<endpoint_id>/access_list``
        """
        endpoint_id = utils.safe_stringify(endpoint_id)
        log.info(
            f"TransferClient.endpoint_manager_endpoint_acl_list({endpoint_id}, ...)"
        )
        path = self.qjoin_path(
            "endpoint_manager", "endpoint", endpoint_id, "access_list"
        )
        return IterableTransferResponse(self.get(path, query_params=query_params))

    #
    # endpoint manager task methods
    #

    @utils.doc_api_method(
        "Advanced Endpoint Management: Get tasks",
        "transfer/advanced_endpoint_management/#get_tasks",
    )
    @paging.has_paginator(paging.LastKeyPaginator, items_key="DATA")
    def endpoint_manager_task_list(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        r"""
        Get a list of tasks visible via ``activity_monitor`` role, as opposed
        to tasks owned by the current user.

        ``GET endpoint_manager/task_list``

        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional

        **Filters**

        The following filters are supported (passed as keyword arguments in
        ``query_params``). For any query that doesn’t specify a filter_status
        that is a subset of ("ACTIVE", "INACTIVE"), at least one of
        filter_task_id or filter_endpoint is required.

        ====================== ================ ========================
        Query Parameter        Filter Type      Description
        ====================== ================ ========================
        filter_status          equality list    |filter_status|
        filter_task_id         equality list    |filter_task_id|
        filter_owner_id        equality         |filter_owner_id|
        filter_endpoint        equality         |filter_endpoint|
        filter_is_paused       boolean equality |filter_is_paused|
        filter_completion_time datetime range   |filter_completion_time|
        filter_min_faults      int              |filter_min_faults|
        filter_local_user      equality         |filter_local_user|
        ====================== ================ ========================

        .. |filter_status| replace::
           Comma separated list of task statuses.  Return only tasks with any of the
           specified statuses. Note that in-progress tasks will have status "ACTIVE" or
           "INACTIVE", and completed tasks will have status "SUCCEEDED" or "FAILED".

        .. |filter_task_id| replace::
           Comma separated list of task_ids, limit 50. Return only tasks with any of
           the specified ids. If any of the specified tasks do not involve an endpoint
           the user has an appropriate role for, a ``PermissionDenied`` error will be
           returned. This filter can't be combined with any other filter.  If another
           filter is passed, a ``BadRequest`` will be returned.

        .. |filter_owner_id| replace::
           A Globus Auth identity id. Limit results to tasks submitted by the specified
           identity, or linked to the specified identity, at submit time.  Returns
           ``UserNotFound`` if the identity does not exist or has never used the Globus
           Transfer service. If no tasks were submitted by this user to an endpoint the
           current user has an appropriate role on, an empty result set will be
           returned. Unless filtering for running tasks (i.e. ``filter_status`` is a
           subset of ("ACTIVE", "INACTIVE"), ``filter_endpoint`` is required when using
           ``filter_owner_id``.

        .. |filter_endpoint| replace::
           Single endpoint id or canonical name. Using canonical name is deprecated.
           Return only tasks with a matching source or destination endpoint or matching
           source or destination host endpoint.

        .. |filter_is_paused| replace::
           Return only tasks with the specified ``is_paused`` value. Requires that
           ``filter_status`` is also passed and contains a subset of "ACTIVE" and
           "INACTIVE". Completed tasks always have ``is_paused`` equal to "false" and
           filtering on their paused state is not useful and not supported.  Note that
           pausing is an async operation, and after a pause rule is inserted it will
           take time before the is_paused flag is set on all affected tasks. Tasks
           paused by id will have the ``is_paused`` flag set immediately.

        .. |filter_completion_time| replace::
           Start and end date-times separated by a comma. Each datetime should be
           specified as a string in ISO 8601 format: ``YYYY-MM-DDTHH:MM:SS``, where the
           "T" separating date and time is literal, with optional \+/-HH:MM for
           timezone.  If no timezone is specified, UTC is assumed, or a trailing "Z" can
           be specified to make UTC explicit. A space can be used between the date and
           time instead of a space.  A blank string may be used for either the start or
           end (but not both) to indicate no limit on that side.  Returns only complete
           tasks with ``completion_time`` in the specified range. If the end date is
           blank, it will also include all active tasks, since they will complete some
           time in the future.

        .. |filter_min_faults| replace::
           Minimum number of cumulative faults, inclusive.  Return only tasks with
           ``faults >= N``, where N is the filter value.  Use ``filter_min_faults=1`` to
           find all tasks with at least one fault.  Note that many errors are not fatal
           and the task may still be successful even if ``faults >= 1``.

        .. |filter_local_user| replace::
           A valid username for the target system running the endpoint, as a utf8
           encoded string. Requires that ``filter_endpoint`` is also set. Return only
           tasks that have successfully fetched the local user from the endpoint, and
           match the values of ``filter_endpoint`` and ``filter_local_user`` on the
           source or on the destination.

        **Examples**

        Fetch some tasks and print some basic info:

        >>> tc = TransferClient(...)
        >>> for task in tc.endpoint_manager_task_list(filter_status="ACTIVE"):
        >>>     print("Task({}): {} -> {}\n  was submitted by\n  {}".format(
        >>>         task["task_id"], task["source_endpoint"],
        >>>         task["destination_endpoint"], task["owner_string"]))

        Do that same operation on *all* tasks visible via ``activity_monitor``
        status:

        >>> tc = TransferClient(...)
        >>> for page in tc.paginated.endpoint_manager_task_list(
        >>>     filter_status="ACTIVE"
        >>> ):
        >>>     for task in page:
        >>>         print("Task({}): {} -> {}\n  was submitted by\n  {}".format(
        >>>             task["task_id"], task["source_endpoint"],
        >>>             task["destination_endpoint"), task["owner_string"])
        """
        log.info("TransferClient.endpoint_manager_task_list(...)")
        path = self.qjoin_path("endpoint_manager", "task_list")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get task as admin", "transfer/advanced_endpoint_management/#get_task"
    )
    def endpoint_manager_get_task(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Get task info as an admin. Requires activity monitor effective role on
        the destination endpoint of the task.

        ``GET /endpoint_manager/task/<task_id>``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_get_task({task_id}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Get task events as admin",
        "transfer/advanced_endpoint_management/#get_task_events",
    )
    @paging.has_paginator(
        paging.LimitOffsetTotalPaginator,
        items_key="DATA",
        get_page_size=_get_page_size,
        max_total_results=1000,
        page_size=1000,
    )
    def endpoint_manager_task_event_list(
        self,
        task_id: UUIDLike,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        """
        List events (for example, faults and errors) for a given task as an
        admin. Requires activity monitor effective role on the destination
        endpoint of the task.

        ``GET /task/<task_id>/event_list``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param limit: limit the number of results
        :type limit: int, optional
        :param offset: offset used in paging
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_task_event_list({task_id}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id, "event_list")
        if query_params is None:
            query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if offset is not None:
            query_params["offset"] = offset
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get task pause info as admin",
        "transfer/advanced_endpoint_management/#get_task_pause_info_as_admin",
    )
    def endpoint_manager_task_pause_info(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Get details about why a task is paused as an admin. Requires activity
        monitor effective role on the destination endpoint of the task.

        ``GET /endpoint_manager/task/<task_id>/pause_info``
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_task_pause_info({task_id}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id, "pause_info")
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Get task successful transfers as admi",
        "transfer/advanced_endpoint_management/#get_task_successful_transfers_as_admin",
    )
    @paging.has_paginator(paging.MarkerPaginator, items_key="DATA")
    def endpoint_manager_task_successful_transfers(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get the successful file transfers for a completed Task as an admin.

        ``GET /endpoint_manager/task/<task_id>/successful_transfers``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        task_id = utils.safe_stringify(task_id)
        log.info(
            "TransferClient.endpoint_manager_task_successful_transfers(%s, ...)",
            task_id,
        )
        path = self.qjoin_path(
            "endpoint_manager", "task", task_id, "successful_transfers"
        )
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Get task skipped errors as admin",
        "transfer/advanced_endpoint_management/#get_task_skipped_errors_as_admin",
    )
    def endpoint_manager_task_skipped_errors(
        self, task_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> IterableTransferResponse:
        """
        Get skipped errors for a completed Task as an admin.

        ``GET /endpoint_manager/task/<task_id>/skipped_errors``

        :param task_id: The ID of the task to inspect.
        :type task_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        task_id = utils.safe_stringify(task_id)
        log.info(f"TransferClient.endpoint_manager_task_skipped_errors({task_id}, ...)")
        path = self.qjoin_path("endpoint_manager", "task", task_id, "skipped_errors")
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Cancel tasks as admin", "transfer/advanced_endpoint_management/#admin_cancel"
    )
    def endpoint_manager_cancel_tasks(
        self,
        task_ids: Iterable[UUIDLike],
        message: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        Cancel a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_cancel``

        :param task_ids: List of task ids to cancel.
        :type task_ids: iterable of str
        :param message: Message given to all users who's tasks have been canceled.
        :type message: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        log.info(
            f"TransferClient.endpoint_manager_cancel_tasks({str_task_ids}, {message})"
        )
        data = {"message": message, "task_id_list": str_task_ids}
        path = self.qjoin_path("endpoint_manager", "admin_cancel")
        return self.post(path, data=data, query_params=query_params)

    @utils.doc_api_method(
        "Get cancel status by ID",
        "transfer/advanced_endpoint_management/#get_cancel_status_by_id",
    )
    def endpoint_manager_cancel_status(
        self, admin_cancel_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Get the status of an an admin cancel (result of
        endpoint_manager_cancel_tasks).

        ``GET /endpoint_manager/admin_cancel/<admin_cancel_id>``

        :param admin_cancel_id: The ID of the the cancel job to inspect.
        :type admin_cancel_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        admin_cancel_id = utils.safe_stringify(admin_cancel_id)
        log.info(f"TransferClient.endpoint_manager_cancel_status({admin_cancel_id})")
        path = self.qjoin_path("endpoint_manager", "admin_cancel", admin_cancel_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Pause tasks as admin",
        "transfer/advanced_endpoint_management/#pause_tasks_as_admin",
    )
    def endpoint_manager_pause_tasks(
        self,
        task_ids: Iterable[UUIDLike],
        message: str,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        Pause a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_pause``

        :param task_ids: List of task ids to pause.
        :type task_ids: iterable of str
        :param message: Message given to all users who's tasks have been paused.
        :type message: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        log.info(
            f"TransferClient.endpoint_manager_pause_tasks({str_task_ids}, {message})"
        )
        data = {"message": message, "task_id_list": str_task_ids}
        path = self.qjoin_path("endpoint_manager", "admin_pause")
        return self.post(path, data=data, query_params=query_params)

    @utils.doc_api_method(
        "Resume tasks as admin",
        "transfer/advanced_endpoint_management/#resume_tasks_as_admin",
    )
    def endpoint_manager_resume_tasks(
        self,
        task_ids: Iterable[UUIDLike],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> response.GlobusHTTPResponse:
        """
        Resume a list of tasks as an admin. Requires activity manager effective
        role on the task(s) source or destination endpoint(s).

        ``POST /endpoint_manager/admin_resume``

        :param task_ids: List of task ids to resume.
        :type task_ids: iterable of str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        str_task_ids = [utils.safe_stringify(i) for i in task_ids]
        log.info(f"TransferClient.endpoint_manager_resume_tasks({str_task_ids})")
        data = {"task_id_list": str_task_ids}
        path = self.qjoin_path("endpoint_manager", "admin_resume")
        return self.post(path, data=data, query_params=query_params)

    #
    # endpoint manager pause rule methods
    #

    @utils.doc_api_method(
        "Get pause rules", "transfer/advanced_endpoint_management/#get_pause_rules"
    )
    def endpoint_manager_pause_rule_list(
        self,
        filter_endpoint: Optional[UUIDLike] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> IterableTransferResponse:
        """
        Get a list of pause rules on endpoints that the current user has the
        activity monitor effective role on.

        ``GET /endpoint_manager/pause_rule_list``

        :param filter_endpoint: An endpoint ID. Limit results to rules on endpoints
            hosted by this endpoint. Must be activity monitor on this endpoint, not just
            the hosted endpoints.
        :type filter_endpoint: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        log.info("TransferClient.endpoint_manager_pause_rule_list(...)")
        path = self.qjoin_path("endpoint_manager", "pause_rule_list")
        if query_params is None:
            query_params = {}
        if filter_endpoint is not None:
            query_params["filter_endpoint"] = utils.safe_stringify(filter_endpoint)
        return IterableTransferResponse(self.get(path, query_params=query_params))

    @utils.doc_api_method(
        "Create pause rule", "transfer/advanced_endpoint_management/#create_pause_rule"
    )
    def endpoint_manager_create_pause_rule(
        self, data: Optional[dict]
    ) -> response.GlobusHTTPResponse:
        """
        Create a new pause rule. Requires the activity manager effective role
        on the endpoint defined in the rule.

        ``POST /endpoint_manager/pause_rule``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "DATA_TYPE": "pause_rule",
        >>>   "message": "Message to users explaining why tasks are paused",
        >>>   "endpoint_id": "339abc22-aab3-4b45-bb56-8d40535bfd80",
        >>>   "identity_id": None,  # affect all users on endpoint
        >>>   "start_time": None  # start now
        >>> }
        >>> create_result = tc.endpoint_manager_create_pause_rule(ep_data)
        >>> rule_id = create_result["id"]
        """
        log.info("TransferClient.endpoint_manager_create_pause_rule(...)")
        path = self.qjoin_path("endpoint_manager", "pause_rule")
        return self.post(path, data=data)

    @utils.doc_api_method(
        "Get pause rule", "transfer/advanced_endpoint_management/#get_pause_rule"
    )
    def endpoint_manager_get_pause_rule(
        self, pause_rule_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Get an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.

        ``GET /endpoint_manager/pause_rule/<pause_rule_id>``

        :param pause_rule_id: ID of pause rule to get.
        :type pause_rule_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_get_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.get(path, query_params=query_params)

    @utils.doc_api_method(
        "Update pause rule", "transfer/advanced_endpoint_management/#update_pause_rule"
    )
    def endpoint_manager_update_pause_rule(
        self, pause_rule_id: UUIDLike, data: Optional[dict]
    ) -> response.GlobusHTTPResponse:
        """
        Update an existing pause rule by ID. Requires the activity manager
        effective role on the endpoint defined in the rule.
        Note that non update-able fields in data will be ignored.

        ``PUT /endpoint_manager/pause_rule/<pause_rule_id>``

        **Examples**

        >>> tc = globus_sdk.TransferClient(...)
        >>> rule_data = {
        >>>   "message": "Update to pause, reads are now allowed.",
        >>>   "pause_ls": False,
        >>>   "pause_task_transfer_read": False
        >>> }
        >>> update_result = tc.endpoint_manager_update_pause_rule(ep_data)
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_update_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.put(path, data=data)

    @utils.doc_api_method(
        "Delete pause rule", "transfer/advanced_endpoint_management/#delete_pause_rule"
    )
    def endpoint_manager_delete_pause_rule(
        self, pause_rule_id: UUIDLike, query_params: Optional[Dict[str, Any]] = None
    ) -> response.GlobusHTTPResponse:
        """
        Delete an existing pause rule by ID. Requires the user to see the
        "editible" field of the rule as True. Any tasks affected by this rule
        will no longer be once it is deleted.

        ``DELETE /endpoint_manager/pause_rule/<pause_rule_id>``

        :param pause_rule_id: The ID of the pause rule to delete.
        :type pause_rule_id: str
        :param query_params: Any additional parameters will be passed through
            as query params.
        :type query_params: dict, optional
        """
        pause_rule_id = utils.safe_stringify(pause_rule_id)
        log.info(f"TransferClient.endpoint_manager_delete_pause_rule({pause_rule_id})")
        path = self.qjoin_path("endpoint_manager", "pause_rule", pause_rule_id)
        return self.delete(path, query_params=query_params)
