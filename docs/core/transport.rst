Transport Layer
===============

The transport consists of a transport object (
:class:`RequestsTransport <globus_sdk.transport.RequestsTransport>`), but also
tooling for handling retries. It is possible to either register custom retry
check methods, or to override the
:class:`RetryPolicy <globus_sdk.transport.RetryPolicy>` used by the
transport in order to customize this behavior.

Transport
~~~~~~~~~

.. autoclass:: globus_sdk.transport.RequestsTransport
   :members: request
   :member-order: bysource

Retries
~~~~~~~

.. autoclass:: globus_sdk.transport.RetryPolicy
   :members:
   :member-order: bysource

.. autoclass:: globus_sdk.transport.RetryContext
   :members:
   :member-order: bysource

Data Encoders
~~~~~~~~~~~~~

.. autoclass:: globus_sdk.transport.RequestEncoder
   :members:
   :member-order: bysource

.. autoclass:: globus_sdk.transport.JSONRequestEncoder
   :members:
   :member-order: bysource

.. autoclass:: globus_sdk.transport.FormRequestEncoder
   :members:
   :member-order: bysource
