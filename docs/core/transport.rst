Transport Layer
===============

The transport consists of a transport object (
:class:`RequestsTransport <globus_sdk.transport.RequestsTransport>`), but also
tooling for handling retries. It is possible to either register custom retry
check methods, or to override the Transport used by a client in order to
customize this behavior.

Transport
~~~~~~~~~

.. autoclass:: globus_sdk.transport.RequestsTransport
   :members: request
   :member-order: bysource

Retries
~~~~~~~

These are the components used by the ``RequestsTransport`` to implement retry
logic.

.. autoclass:: globus_sdk.transport.RetryContext
   :members:
   :member-order: bysource

.. autoclass:: globus_sdk.transport.RetryCheckResult
   :members:
   :member-order: bysource

.. data:: globus_sdk.transport.RetryCheck

   The type for a retry check, a callable which takes a
   ``RetryContext`` and returns a ``RetryCheckResult``. Equivalent to
   ``Callable[[globus_sdk.transport.RetryContext], globus_sdk.transport.RetryCheckResult]``

.. autoclass:: globus_sdk.transport.RetryCheckRunner
   :members:
   :member-order: bysource

.. autoclass:: globus_sdk.transport.RetryCheckFlags
   :members:
   :member-order: bysource

.. autodecorator:: globus_sdk.transport.set_retry_check_flags

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
