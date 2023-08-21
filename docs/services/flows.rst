Globus Flows
=============

.. currentmodule:: globus_sdk

The Flows service allows users to create automation workflows or, simply, "flows".
When a flow is started, it must be authorized to perform actions on the user's behalf.

Because a running flow can perform actions on the user's behalf,
the Globus SDK has two client classes that can interact with the Flows service:
a :class:`FlowsClient` and a :class:`SpecificFlowClient`.
They differ in what scopes and user consents they require:

*   The :class:`FlowsClient` is able to create, update, and delete flows.
    It is also able to gather information about flows and runs.

    Users must consent to allow the client application to administer flows and runs.

*   The :class:`SpecificFlowClient` is able to start a specific flow.
    Once started, if the run becomes inactive (or "becomes paused") for any reason,
    this class is able to resume the run, too.

    Users must consent to allow the specific flow to perform actions on their behalf.


.. autoclass:: FlowsClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

.. autoclass:: SpecificFlowClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Client Errors
-------------

When an error occurs, a :class:`FlowsClient` will raise a ``FlowsAPIError``.

.. autoclass:: FlowsAPIError
   :members:
   :show-inheritance:

