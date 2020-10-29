Common API
==========

All service clients support the low level interface, provided by the
``BaseClient``.

.. autoclass:: globus_sdk.base.BaseClient
   :members: get, put, post, delete, set_app_name
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
