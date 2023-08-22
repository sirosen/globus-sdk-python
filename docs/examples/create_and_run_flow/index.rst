Create & Run a Flow
===================

These examples guide you through creating and running a **flow** using the Globus
Flows service.

Note that users are restricted to only creating one **flow** unless covered by a
Globus subscription. Therefore, these examples will also include an option to
delete your **flow**.


Create and Delete Hello World Flow
----------------------------------

This script provides commands to create, list, and delete your **flows**.
The **flow** definition used for it is simple and baked into the script, but this
demonstrates the minimal **flow** creation and deletion process.

.. literalinclude:: manage_flow_minimal.py
    :caption: ``manage_flow_minimal.py`` [:download:`download <manage_flow_minimal.py>`]
    :language: python


Run a Flow
----------

This next example is distinct. It runs a flow but has no capability to create
or delete a flow. Note how ``SpecificFlowClient`` is used -- this class allows
users to access the flow-specific scope and provides the methods associated
with that scope of running **flows** and resuming **runs**.

The login code is slightly different from the previous example, as it has to
key off of the Flow ID in order to act appropriately.

.. literalinclude:: run_flow_minimal.py
    :caption: ``run_flow_minimal.py`` [:download:`download <run_flow_minimal.py>`]
    :language: python


Create, Delete, and Run Flows
-----------------------------

The following example combines the previous two.
It has to further enhance the login code to account for the two different
styles of login which it supports, but minimal other adjustments are needed.

Depending on the operation chosen, either the ``FlowsClient`` or the
``SpecificFlowClient`` will be used, and the login flow will also be
appropriately parametrized.

.. literalinclude:: manage_flow.py
    :caption: ``manage_flow.py`` [:download:`download <manage_flow.py>`]
    :language: python
