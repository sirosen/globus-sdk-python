Globus Groups
=============

.. currentmodule:: globus_sdk

.. autoclass:: GroupsClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

These helper objects make it easier to create and submit data to a :class:`GroupsClient`.
Additionally, they may be used in concert with the :class:`GroupsManager` to perform
operations.

These enums define values which can be passed to other helpers:

.. autoclass:: GroupMemberVisibility
    :members:
    :undoc-members:

.. autoclass:: GroupRequiredSignupFields
    :members:
    :undoc-members:

.. autoclass:: GroupRole
    :members:
    :undoc-members:

.. autoclass:: GroupVisibility
    :members:
    :undoc-members:

Payload Types
~~~~~~~~~~~~~

A :class:`BatchMembershipActions` defines how to formulate requests to add, remove, or modify
memberships in a group. It can be used to formulate multiple operations to submit in a single
request to the service.

.. autoclass:: BatchMembershipActions
   :members:

A :class:`GroupPolicies` object defines the various policies which can be set on a
group. It can be used with the :class:`GroupsClient` or the :class:`GroupsManager`.

.. autoclass:: GroupPolicies
   :members:

High-Level Client Wrappers
~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`GroupsManager` is a high-level helper which wraps a :class:`GroupsClient`. Many common
operations which require assembling a :class:`BatchMembershipActions` and submitting the
result can be achieved with a single method-call on a :class:`GroupsManager`.

.. autoclass:: GroupsManager
   :members:

Client Errors
-------------

When an error occurs, a :class:`GroupsClient` will raise this type of error:

.. autoclass:: GroupsAPIError
   :members:
   :show-inheritance:
