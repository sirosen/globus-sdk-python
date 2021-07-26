from typing import List, Optional


class ScopeBuilder:
    """
    Utility class for creating scope strings for a specified resource server.

    :param resource_server: The identifier, usually a domain name or a UUID, for the
        resource server to return scopes for.
    :type resource_server: str
    :param known_scopes: A list of scope names to pre-populate on this instance. This
        will set attributes on the instance using the URN scope format.
    :type known_scopes: list, optional
    """

    def __init__(
        self, resource_server: str, known_scopes: Optional[List[str]] = None
    ) -> None:
        self.resource_server = resource_server
        self._known_scopes = known_scopes
        if known_scopes:
            for scope_name in known_scopes:
                setattr(self, scope_name, self.urn_scope_string(scope_name))

    def urn_scope_string(self, scope_name: str) -> str:
        """
        Return a complete string representing the scope with a given name for this
        client, in the Globus Auth URN format.

        Note that this module already provides many such scope strings for use with
        Globus services.

        **Examples**

        >>> sb = ScopeBuilder("transfer.api.globus.org")
        >>> sb.urn_scope_string("transfer.api.globus.org", "all")
        "urn:globus:auth:scope:transfer.api.globus.org:all"

        :param scope_name: The short name for the scope involved.
        :type scope_name: str
        """
        return f"urn:globus:auth:scope:{self.resource_server}:{scope_name}"

    def url_scope_string(self, scope_name: str) -> str:
        """
        Return a complete string representing the scope with a given name for this
        client, in URL format.

        **Examples**

        >>> sb = ScopeBuilder("actions.globus.org")
        >>> sb.url_scope_string("actions.globus.org", "hello_world")
        "https://auth.globus.org/scopes/actions.globus.org/hello_world"

        :param scope_name: The short name for the scope involved.
        :type scope_name: str
        """
        return f"https://auth.globus.org/scopes/{self.resource_server}/{scope_name}"


class GCSScopeBuilder(ScopeBuilder):
    """
    A ScopeBuilder with a named property for the GCS data_access scope.

    **Examples**

    >>> sb = GCSScopeBuilder("xyz")
    >>> da_scope = sb.data_access_scope
    """

    @property
    def data_access_scope(self) -> str:
        return self.url_scope_string("data_access")


class _AuthScopesBuilder(ScopeBuilder):
    openid: str = "openid"
    email: str = "email"
    profile: str = "profile"


AuthScopes = _AuthScopesBuilder(
    "auth.globus.org",
    known_scopes=[
        "view_authentications",
        "view_clients",
        "view_clients_and_scopes",
        "view_identities",
        "view_identity_set",
    ],
)
"""Globus Auth scopes.

.. listknownscopes:: globus_sdk.scopes.AuthScopes
    add_scopes=openid,email,profile
    example_scope=view_identity_set
"""


GroupsScopes = ScopeBuilder(
    "groups.api.globus.org",
    known_scopes=[
        "all",
        "view_my_groups_and_memberships",
    ],
)
"""Groups scopes.

.. listknownscopes:: globus_sdk.scopes.GroupsScopes
"""


NexusScopes = ScopeBuilder(
    "nexus.api.globus.org",
    known_scopes=[
        "groups",
    ],
)
"""Nexus scopes (internal use only).

.. listknownscopes:: globus_sdk.scopes.NexusScopes
"""

SearchScopes = ScopeBuilder(
    "search.api.globus.org",
    known_scopes=[
        "all",
        "globus_connect_server",
        "ingest",
        "search",
    ],
)
"""Globus Search scopes.

.. listknownscopes:: globus_sdk.scopes.SearchScopes
"""

TransferScopes = ScopeBuilder(
    "transfer.api.globus.org",
    known_scopes=[
        "all",
        "gcp_install",
        "monitor_ongoing",
    ],
)
"""Globus Transfer scopes.

.. listknownscopes:: globus_sdk.scopes.TransferScopes
"""
