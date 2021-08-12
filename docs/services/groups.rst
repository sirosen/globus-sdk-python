.. module:: globus_sdk.groups


Globus Groups
=============

.. autoclass:: globus_sdk.GroupsClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

These helper objects make it easier to create and submit data to a ``GroupsClient``.
Additionally, they may be used in concert with the ``GroupsManager`` to perform
operations.

These enums define values which can be passed to other helpers:

.. autoclass:: GroupMemberVisibility
    :members:

.. autoclass:: GroupRequiredSignupFields
    :members:

.. autoclass:: GroupRole
    :members:

.. autoclass:: GroupVisibility
    :members:

A ``BatchMembershipActions`` defines how to formulate requests to add, remove, or modify
memberships in a group. It can be used to formulate multiple operations to submit in a single
request to the service.

.. autoclass:: globus_sdk.BatchMembershipActions
   :members:

The ``GroupsManager`` is a high-level helper which wraps a ``GroupsClient``. Many common
operations which require assembling a ``BatchMembershipActions`` and submitting the
result can be achieved with a single method-call on a ``GroupsManager``.

.. autoclass:: globus_sdk.GroupsManager
   :members:

Client Errors
-------------

When an error occurs, a ``GroupsClient`` will raise this type of error:

.. autoclass:: globus_sdk.GroupsAPIError
   :members:
   :show-inheritance:
