Globus Flows
=============

.. currentmodule:: globus_sdk

The Flows service allows users to create automation workflows (or, simply, "flows").
When a flow is started, it must be authorized to perform actions on the user's behalf.

Because a running flow (or, simply, a "run") can perform actions on the user's behalf,
the Globus SDK has two client classes that can interact with the Flows service:
a :class:`FlowsClient` and a :class:`SpecificFlowClient`.
They differ in what operations they can perform and, as a result,
what scopes they require:

*   :class:`FlowsClient` is able to create, update, and delete flows.
    It is also able to retrieve information about flows and runs.

    Users must consent to allow the client application to administer flows and runs.
    See :class:`FlowsClient.scopes` for a complete list of scopes.

*   :class:`SpecificFlowClient` must be instantiated with a specific flow ID
    so it can construct the scope associated with the flow.
    It is then able to start that specific flow.
    If a run associated with the flow becomes inactive for any reason,
    it is able to resume the run, too.

    Users must consent to allow the specific flow to perform actions on their behalf.
    The specific flow scope can be accessed via ``SpecificFlowClient.scopes.user``
    after the :class:`SpecificFlowClient` has been instantiated.

Applications that create and then start a flow would therefore need to use both classes.


..  autoclass:: FlowsClient
    :members:
    :member-order: bysource
    :show-inheritance:
    :exclude-members: error_class, scopes

    ..  attribute:: scopes

        ..  listknownscopes:: globus_sdk.scopes.FlowsScopes
            :base_name: FlowsClient.scopes

..  autoclass:: SpecificFlowClient
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

Responses
---------

.. autoclass:: IterableFlowsResponse
   :members:
   :show-inheritance:
