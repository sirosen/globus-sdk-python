from __future__ import annotations

import logging
import sys
import typing as t

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import client, exc, utils
from globus_sdk._types import UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.response import GlobusHTTPResponse, IterableResponse
from globus_sdk.scopes import AuthScopes

from .._common import get_jwk_data, pem_decode_jwk_data
from ..errors import AuthAPIError
from ..response import (
    GetIdentitiesResponse,
    GetIdentityProvidersResponse,
    GetProjectsResponse,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

log = logging.getLogger(__name__)


class AuthClient(client.BaseClient):
    """
    A client for using the
    `Globus Auth API <https://docs.globus.org/api/auth/>`_

    This class provides helper methods for most common resources in the
    Auth API, and the common low-level interface from
    :class:`BaseClient <globus_sdk.client.BaseClient>` of ``get``, ``put``,
    ``post``, and ``delete`` methods, which can be used to access any API
    resource.

    **Examples**

    Initializing an ``AuthClient`` to authenticate a user making calls to the
    Globus Auth service with an access token takes the form

    >>> from globus_sdk import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))

    Other authorizers, most notably ``RefreshTokenAuthorizer``, are also supported.

    .. automethodlist:: globus_sdk.AuthClient
    """

    service_name = "auth"
    error_class = AuthAPIError
    scopes = AuthScopes

    def __init__(
        self,
        client_id: UUIDLike | None = None,
        environment: str | None = None,
        base_url: str | None = None,
        authorizer: GlobusAuthorizer | None = None,
        app_name: str | None = None,
        transport_params: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(
            environment=environment,
            base_url=base_url,
            authorizer=authorizer,
            app_name=app_name,
            transport_params=transport_params,
        )

        self._client_id = str(client_id) if client_id is not None else None
        if client_id is not None:
            exc.warn_deprecated(
                "The client_id parameter is no longer accepted by `AuthClient` / "
                "`AuthClient`. When creating a client which represents an "
                "application, use `NativeAppAuthClient` or "
                "`ConfidentialAppAuthClient` instead."
            )

    # this attribute is preserved for compatibility, but will be removed in a
    # future release
    @property
    def client_id(self) -> str | None:
        exc.warn_deprecated(
            "The client_id attribute on `AuthClient` / "
            "`AuthClient` is deprecated. "
            "For clients with client IDs, use `NativeAppAuthClient` or "
            "`ConfidentialAppAuthClient` instead."
        )
        return self._client_id

    @client_id.setter
    def client_id(self, value: UUIDLike) -> None:
        exc.warn_deprecated(
            "The client_id attribute on `AuthClient` / "
            "`AuthClient` is deprecated. "
            "For clients with client IDs, use `NativeAppAuthClient` or "
            "`ConfidentialAppAuthClient` instead."
        )
        self._client_id = str(value) if value is not None else None

    # FYI: this get_openid_configuration method is duplicated in AuthLoginBaseClient
    # if this code is modified, please update that copy as well
    # this will ideally be resolved in a future SDK version by making this the only copy
    def get_openid_configuration(self) -> GlobusHTTPResponse:
        """
        Fetch the OpenID Connect configuration data from the well-known URI for Globus
        Auth.
        """
        log.info("Fetching OIDC Config")
        return self.get("/.well-known/openid-configuration")

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: Literal[True],
    ) -> RSAPublicKey:
        ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any],
        *,
        as_pem: Literal[False],
    ) -> dict[str, t.Any]:
        ...

    # FYI: this get_jwk method is duplicated in AuthLoginBaseClient
    # if this code is modified, please update that copy as well
    # this will ideally be resolved in a future SDK version by making this the only copy
    def get_jwk(
        self,
        openid_configuration: None | GlobusHTTPResponse | dict[str, t.Any] = None,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]:
        """
        Fetch the Globus Auth JWK.

        Returns either a dict or an RSA Public Key object depending on ``as_pem``.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :type openid_configuration: dict or GlobusHTTPResponse
        :param as_pem: Decode the JWK to an RSA PEM key, typically for JWT decoding
        :type as_pem: bool
        """
        if openid_configuration is None:
            log.debug("No OIDC Config provided, autofetching...")
            openid_configuration = self.get_openid_configuration()
        jwk_data = get_jwk_data(
            fget=self.get, openid_configuration=openid_configuration
        )
        return pem_decode_jwk_data(jwk_data=jwk_data) if as_pem else jwk_data

    def userinfo(self) -> GlobusHTTPResponse:
        """
        Call the Userinfo endpoint of Globus Auth.
        Userinfo is specified as part of the OpenID Connect (OIDC) standard,
        and Globus Auth's Userinfo is OIDC-compliant.

        The exact data returned will depend upon the set of OIDC-related scopes
        which were used to acquire the token being used for this call. For
        details, see the **API Info** below.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: python

                    ac = AuthClient(...)
                    info = ac.oauth2_userinfo()
                    print(
                        'Effective Identity "{info["sub"]}" has '
                        f'Full Name "{info["name"]}" and '
                        f'Email "{info["email"]}"'
                    )

            .. tab-item:: API Info

                ``GET /v2/oauth2/userinfo``

                .. extdoclink:: Get Userinfo
                    :ref: auth/reference/#get_or_post_v2_oauth2_userinfo_resource
        """
        log.info("Looking up OIDC-style Userinfo from Globus Auth")
        return self.get("/v2/oauth2/userinfo")

    def oauth2_userinfo(self) -> GlobusHTTPResponse:
        """
        A deprecated alias for ``userinfo``.
        """
        exc.warn_deprecated(
            "The method `oauth2_userinfo` is deprecated. Use `userinfo` instead."
        )
        return self.userinfo()

    def get_identities(
        self,
        *,
        usernames: t.Iterable[str] | str | None = None,
        ids: t.Iterable[UUIDLike] | UUIDLike | None = None,
        provision: bool = False,
        query_params: dict[str, t.Any] | None = None,
    ) -> GetIdentitiesResponse:
        r"""
        Given ``usernames=<U>`` or (exclusive) ``ids=<I>`` as keyword
        arguments, looks up identity information for the set of identities
        provided.
        ``<U>`` and ``<I>`` in this case are comma-delimited strings listing
        multiple Identity Usernames or Identity IDs, or iterables of strings,
        each of which is an Identity Username or Identity ID.

        If Globus Auth's identity auto-provisioning behavior is desired,
        ``provision=True`` may be specified.

        Available with any authentication/client type.

        :param usernames: A username or list of usernames to lookup. Mutually exclusive
            with ``ids``
        :type usernames: str or iterable of str, optional
        :param ids: An identity ID or list of IDs to lookup. Mutually exclusive
            with ``usernames``
        :type ids: str, UUID, or iterable of str or UUID, optional
        :param provision: Create identities if they do not exist, allowing clients to
            get username-to-identity mappings prior to the identity being used
        :type provision: bool
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get by ID
                    >>> r = ac.get_identities(ids="46bd0f56-e24f-11e5-a510-131bef46955c")
                    >>> r.data
                    {
                      'identities': [
                        {
                          'email': None,
                          'id': '46bd0f56-e24f-11e5-a510-131bef46955c',
                          'identity_provider': '7daddf46-70c5-45ee-9f0f-7244fe7c8707',
                          'name': None,
                          'organization': None,
                          'status': 'unused',
                          'username': 'globus@globus.org'
                        }
                      ]
                    }
                    >>> ac.get_identities(
                    ...     ids=",".join(
                    ...         ("46bd0f56-e24f-11e5-a510-131bef46955c", "168edc3d-c6ba-478c-9cf8-541ff5ebdc1c")
                    ...     )
                    ... )
                    >>> # or by usernames
                    >>> ac.get_identities(usernames="globus@globus.org")
                    >>> ac.get_identities(usernames="globus@globus.org,auth@globus.org")

                You could also use iterables:

                .. code-block:: python

                    ac.get_identities(usernames=["globus@globus.org", "auth@globus.org"])

                    ac.get_identities(
                        ids=["46bd0f56-e24f-11e5-a510-131bef46955c", "168edc3d-c6ba-478c-9cf8-541ff5ebdc1c"]
                    )

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for identity in ac.get_identities(usernames=["globus@globus.org", "auth@globus.org"]):
                        print(identity["id"])

            .. tab-item:: API Info

                ``GET /v2/api/identities``

                .. extdoclink:: Get Identities
                    :ref: auth/reference/#v2_api_identities_resources
        """  # noqa: E501

        log.info("Looking up Globus Auth Identities")

        if query_params is None:
            query_params = {}

        # if either of these params has a truthy value, stringify it
        if usernames:
            query_params["usernames"] = utils.commajoin(usernames)
            query_params["provision"] = (
                "false" if str(provision).lower() == "false" else "true"
            )
        if ids:
            query_params["ids"] = utils.commajoin(ids)

        log.debug(f"query_params={query_params}")

        if "usernames" in query_params and "ids" in query_params:
            log.warning(
                "get_identities call with both usernames and "
                "identities set! Expected to result in errors"
            )

        return GetIdentitiesResponse(
            self.get("/v2/api/identities", query_params=query_params)
        )

    def get_identity_providers(
        self,
        *,
        domains: t.Iterable[str] | str | None = None,
        ids: t.Iterable[UUIDLike] | UUIDLike | None = None,
        query_params: dict[str, t.Any] | None = None,
    ) -> GetIdentityProvidersResponse:
        r"""
        Look up information about identity providers by domains or by IDs.

        :param domains: A domain or iterable of domains to lookup. Mutually exclusive
            with ``ids``.
        :type domains: str or iterable of str, optional
        :param ids: An identity provider ID or iterable of IDs to lookup. Mutually exclusive
            with ``domains``.
        :type ids: str, UUID, or iterable of str or UUID, optional
        :param query_params: Any additional parameters to be passed through
            as query params.
        :type query_params: dict, optional

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> # get by ID
                    >>> r = ac.get_identity_providers(ids="41143743-f3c8-4d60-bbdb-eeecaba85bd9")
                    >>> r.data
                    {
                      "identity_providers": [
                        {
                          "alternative_names": [],
                          "name": "Globus ID",
                          "domains": ["globusid.org"],
                          "id": "41143743-f3c8-4d60-bbdb-eeecaba85bd9",
                          "short_name": "globusid"
                        }
                      ]
                    }
                    >>> ac.get_identities(
                    ...     ids=["41143743-f3c8-4d60-bbdb-eeecaba85bd9", "927d7238-f917-4eb2-9ace-c523fa9ba34e"]
                    ... )
                    >>> # or by domain
                    >>> ac.get_identities(domains="globusid.org")
                    >>> ac.get_identities(domains=["globus.org", "globusid.org"])

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for idp in ac.get_identity_providers(domains=["globus.org", "globusid.org"]):
                        print(f"name: {idp['name']}")
                        print(f"id: {idp['id']}")
                        print(f"domains: {idp['domains']}")
                        print()

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_identity_providers

            .. tab-item:: API Info

                ``GET /v2/api/identity_providers``

                .. extdoclink:: Get Identity Providers
                    :ref: auth/reference/#get_identity_providers
        """  # noqa: E501

        log.info("Looking up Globus Auth Identity Providers")

        if query_params is None:
            query_params = {}

        if domains is not None and ids is not None:
            raise exc.GlobusSDKUsageError(
                "AuthClient.get_identity_providers does not take both "
                "'domains' and 'ids'. These are mutually exclusive."
            )
        # if either of these params has a truthy value, stringify it
        # this handles lists of values as well as individual values gracefully
        # letting us consume args whose `__str__` methods produce "the right
        # thing"
        elif domains is not None:
            query_params["domains"] = utils.commajoin(domains)
        elif ids is not None:
            query_params["ids"] = utils.commajoin(ids)
        else:
            log.warning(
                "neither 'domains' nor 'ids' provided to get_identity_providers(). "
                "This can only succeed if 'query_params' were given."
            )

        log.debug(f"query_params={query_params}")
        return GetIdentityProvidersResponse(
            self.get("/v2/api/identity_providers", query_params=query_params)
        )

    #
    # Developer APIs
    #

    def get_projects(self) -> IterableResponse:
        """
        Look up projects on which the authenticated user is an admin.
        Requires the ``manage_projects`` scope.

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> r = ac.get_projects()
                    >>> r.data
                    {
                      'projects": [
                        {
                          'admin_ids": ["41143743-f3c8-4d60-bbdb-eeecaba85bd9"]
                          'contact_email": "support@globus.org",
                          'display_name": "Globus SDK Demo Project",
                          'admin_group_ids": None,
                          'id": "927d7238-f917-4eb2-9ace-c523fa9ba34e",
                          'project_name": "Globus SDK Demo Project",
                          'admins": {
                            'identities": ["41143743-f3c8-4d60-bbdb-eeecaba85bd9"],
                            'groups": [],
                          },
                      ]
                    }

                The result itself is iterable, so you can use it like so:

                .. code-block:: python

                    for project in ac.get_projects():
                        print(f"name: {project['display_name']}")
                        print(f"id: {project['id']}")
                        print()

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.get_projects

            .. tab-item:: API Info

                ``GET /v2/api/projects``

                .. extdoclink:: Get Projects
                    :ref: auth/reference/#get_projects
        """  # noqa: E501
        return GetProjectsResponse(self.get("/v2/api/projects"))

    def create_project(
        self,
        display_name: str,
        contact_email: str,
        *,
        admin_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
        admin_group_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Create a new project. Requires the ``manage_projects`` scope.

        At least one of ``admin_ids`` or ``admin_group_ids`` must be provided.

        :param display_name: The name of the project
        :type display_name: str
        :param contact_email: The email address of the project's point of contact
        :type contact_email: str
        :param admin_ids: A list of user IDs to be added as admins of the project
        :type admin_ids: str or uuid or iterable of str or uuid, optional
        :param admin_group_ids: A list of group IDs to be added as admins of the project
        :type admin_group_ids: str or uuid or iterable of str or uuid, optional

        .. tab-set::

            .. tab-item:: Example Usage

                When creating a project, your account is not necessarily included as an
                admin. The following snippet uses the ``manage_projects`` scope as well
                as the ``openid`` and ``email`` scopes to get the current user ID and
                email address and use those data to setup the project.

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> userinfo = ac.oauth2_userinfo()
                    >>> identity_id = userinfo["sub"]
                    >>> email = userinfo["email"]
                    >>> r = ac.create_project(
                    ...     "My Project",
                    ...     contact_email=email,
                    ...     admin_ids=identity_id,
                    ... )
                    >>> project_id = r["project"]["id"]

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.create_project

            .. tab-item:: API Info

                ``POST /v2/api/projects``

                .. extdoclink:: Create Project
                    :ref: auth/reference/#create_project
        """
        body: dict[str, t.Any] = {
            "display_name": display_name,
            "contact_email": contact_email,
        }
        if admin_ids is not None:
            body["admin_ids"] = list(utils.safe_strseq_iter(admin_ids))
        if admin_group_ids is not None:
            body["admin_group_ids"] = list(utils.safe_strseq_iter(admin_group_ids))
        return self.post("/v2/api/projects", data={"project": body})

    def update_project(
        self,
        project_id: UUIDLike,
        *,
        display_name: str | None = None,
        contact_email: str | None = None,
        admin_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
        admin_group_ids: UUIDLike | t.Iterable[UUIDLike] | None = None,
    ) -> GlobusHTTPResponse:
        """
        Update a project. Requires the ``manage_projects`` scope.

        :param project_id: The ID of the project to update
        :type project_id: str or uuid
        :param display_name: The name of the project
        :type display_name: str
        :param contact_email: The email address of the project's point of contact
        :type contact_email: str
        :param admin_ids: A list of user IDs to be set as admins of the project
        :type admin_ids: str or uuid or iterable of str or uuid, optional
        :param admin_group_ids: A list of group IDs to be set as admins of the project
        :type admin_group_ids: str or uuid or iterable of str or uuid, optional

        .. tab-set::

            .. tab-item:: Example Usage

                The following snippet uses the ``manage_projects`` scope as well
                as the ``email`` scope to get the current user email address and set it
                as a project's contact email:

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> project_id = ...
                    >>> userinfo = ac.oauth2_userinfo()
                    >>> email = userinfo["email"]
                    >>> r = ac.update_project(project_id, contact_email=email)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.update_project

            .. tab-item:: API Info

                ``POST /v2/api/projects``

                .. extdoclink:: Update Project
                    :ref: auth/reference/#update_project
        """
        body: dict[str, t.Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if contact_email is not None:
            body["contact_email"] = contact_email
        if admin_ids is not None:
            body["admin_ids"] = list(utils.safe_strseq_iter(admin_ids))
        if admin_group_ids is not None:
            body["admin_group_ids"] = list(utils.safe_strseq_iter(admin_group_ids))
        return self.put(f"/v2/api/projects/{project_id}", data={"project": body})

    def delete_project(self, project_id: UUIDLike) -> GlobusHTTPResponse:
        """
        Delete a project. Requires the ``manage_projects`` scope.

        :param project_id: The ID of the project to delete
        :type project_id: str or uuid

        .. tab-set::

            .. tab-item:: Example Usage

                .. code-block:: pycon

                    >>> ac = globus_sdk.AuthClient(...)
                    >>> project_id = ...
                    >>> r = ac.delete_project(project_id)

            .. tab-item:: Example Response Data

                .. expandtestfixture:: auth.delete_project

            .. tab-item:: API Info

                ``DELETE /v2/api/projects/{project_id}``

                .. extdoclink:: Delete Project
                    :ref: auth/reference/#delete_project
        """
        return self.delete(f"/v2/api/projects/{project_id}")
