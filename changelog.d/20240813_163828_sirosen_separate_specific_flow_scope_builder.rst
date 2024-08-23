Added
~~~~~

- The scope builder for ``SpecificFlowClient`` is now available for direct
  access and use via ``globus_sdk.scopes.SpecificFlowScopeBuilder``. Callers can
  initialize this class with a ``flow_id`` to get a scope builder for a
  specific flow, e.g., ``SpecificFlowScopeBuilder(flow_id).user``.
  ``SpecificFlowClient`` now uses this class internally. (:pr:`1030`)
