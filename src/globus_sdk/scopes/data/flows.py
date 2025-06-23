from __future__ import annotations

import typing as t
from functools import cached_property

from globus_sdk._types import UUIDLike

from ..collection import (
    DynamicScopeCollection,
    StaticScopeCollection,
    _url_scope,
)
from ..representation import Scope


class FlowsScopes(StaticScopeCollection):
    # The Flows service breaks the scopes/resource server convention: its
    # resource server is a domain name but its scopes are built around the
    # client ID.
    resource_server = "flows.globus.org"
    client_id = "eec9b274-0c81-4334-bdc2-54e90e689b9a"

    all = _url_scope(client_id, "all")
    manage_flows = _url_scope(client_id, "manage_flows")
    view_flows = _url_scope(client_id, "view_flows")
    run = _url_scope(client_id, "run")
    run_status = _url_scope(client_id, "run_status")
    run_manage = _url_scope(client_id, "run_manage")


class _SpecificFlowScopesClassStub(DynamicScopeCollection):
    """
    This stub object ensures that the type deductions for type checkers (e.g. mypy) on
    SpecificFlowClient.scopes are correct.

    Primarily, it should be possible to access the `scopes` attribute, the `user`
    scope, and the `resource_server`, but these usages should raise specific and
    informative runtime errors.

    Our types are therefore less accurate for class-var access, but more accurate for
    instance-var access.
    """

    _scope_names = ("user",)

    def __init__(self) -> None:
        super().__init__("<stub>")

    def __getattribute__(self, name: str) -> t.Any:
        if name == "user":
            _raise_attr_error("scopes")
        if name == "resource_server":
            _raise_attr_error("resource_server")
        return object.__getattribute__(self, name)


def _raise_attr_error(name: str) -> t.NoReturn:
    raise AttributeError(
        f"It is not valid to attempt to access the '{name}' attribute of the "
        "SpecificFlowClient class. "
        f"Instead, instantiate a SpecificFlowClient and access the '{name}' attribute "
        "from that instance."
    )


class SpecificFlowScopes(DynamicScopeCollection):
    """
    This defines the scopes for a single flow (as distinct from the Flows service).

    It primarily provides the `user` scope which is typically needed to start a run of
    a flow.

    Example usage:

    .. code-block:: python

        sc = SpecificFlowScopes("my-flow-id-here")
        flow_scope = sc.user
    """

    _CLASS_STUB = _SpecificFlowScopesClassStub()
    _scope_names = ("user",)

    def __init__(self, flow_id: UUIDLike) -> None:
        self._flow_id = flow_id
        self._str_flow_id = str(flow_id)
        super().__init__(resource_server=self._str_flow_id)

    @cached_property
    def user(self) -> Scope:
        return _url_scope(
            self.resource_server, f"flow_{self._str_flow_id.replace('-', '_')}_user"
        )
