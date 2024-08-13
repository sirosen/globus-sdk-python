from ..builder import ScopeBuilder, ScopeBuilderScopes


class _FlowsScopeBuilder(ScopeBuilder):
    """
    The Flows Service breaks the scopes/resource server convention:
      its resource server is a domain name but its scopes are built around the client id
    Given that there isn't a simple way to support this more generally
      (and we shouldn't encourage supporting this more generally), this class serves to
      build out the scopes accurately specifically for Flows
    """

    def __init__(
        self,
        domain_name: str,
        client_id: str,
        known_scopes: ScopeBuilderScopes = None,
        known_url_scopes: ScopeBuilderScopes = None,
    ) -> None:
        self._client_id = client_id
        super().__init__(
            domain_name, known_scopes=known_scopes, known_url_scopes=known_url_scopes
        )

    def urn_scope_string(self, scope_name: str) -> str:
        return f"urn:globus:auth:scope:{self._client_id}:{scope_name}"

    def url_scope_string(self, scope_name: str) -> str:
        return f"https://auth.globus.org/scopes/{self._client_id}/{scope_name}"


FlowsScopes = _FlowsScopeBuilder(
    "flows.globus.org",
    "eec9b274-0c81-4334-bdc2-54e90e689b9a",
    known_url_scopes=[
        "all",
        "manage_flows",
        "view_flows",
        "run",
        "run_status",
        "run_manage",
    ],
)
"""Globus Flows scopes.

.. listknownscopes:: globus_sdk.scopes.FlowsScopes
"""
