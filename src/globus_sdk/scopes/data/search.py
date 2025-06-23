from ..collection import StaticScopeCollection, _urn_scope


class SearchScopes(StaticScopeCollection):
    resource_server = "search.api.globus.org"

    all = _urn_scope(resource_server, "all")
    globus_connect_server = _urn_scope(resource_server, "globus_connect_server")
    ingest = _urn_scope(resource_server, "ingest")
    search = _urn_scope(resource_server, "search")
