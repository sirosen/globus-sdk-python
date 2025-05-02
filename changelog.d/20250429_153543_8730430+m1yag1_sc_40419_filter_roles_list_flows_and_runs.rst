Added
~~~~~

- ``FlowsClient.list_flows`` and ``FlowsClient.list_runs`` now support the
  ``filter_roles`` parameter to filter results by one or more roles (:pr:`1174`).

Deprecated
~~~~~~~~~~

- ``filter_role`` parameter for ``FlowsClient.list_flows`` is deprecated. Use
  ``filter_roles`` instead (:pr:`1174`).
