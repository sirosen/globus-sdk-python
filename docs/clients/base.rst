Common API
==========

All service clients support the low level interface, provided by the
``BaseClient``, from which all client types inherit.

A client object contains a ``transport``, an object responsible for sending
requests, encoding data, and handling potential retries. It also may include an
optional ``authorizer``, an object responsible for handling token
authentication for requests.

BaseClient
----------

.. autoclass:: globus_sdk.base.BaseClient
   :members: retry_policy, get, put, post, patch, delete, request
   :member-order: bysource

Transport Layer
---------------

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

Responses
---------

Unless noted otherwise, all method return values for Globus SDK Clients are
``GlobusResponse`` objects.

Some ``GlobusResponse`` objects are iterables.
In those cases, their contents will also be ``GlobusResponse`` objects.

To customize client methods with additional detail, the SDK uses subclasses of
``GlobusResponse``.
For example the ``GlobusHTTPResponse`` attaches HTTP response information.

Generic Response Classes
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: globus_sdk.response.GlobusResponse
   :members:

.. autoclass:: globus_sdk.response.GlobusHTTPResponse
   :members:
   :show-inheritance:
