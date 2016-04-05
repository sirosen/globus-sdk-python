.. _api:

Developer Interface
===================

.. module:: globus_sdk

Common Low Level Interface
--------------------------

All service clients support the low level interface, provides by the
BaseClient.

.. autoclass:: globus_sdk.base.BaseClient
   :members: get, put, post, delete, set_auth_token, set_auth_basic

Transfer High Level Interface
-----------------------------

.. autoclass:: globus_sdk.TransferClient
   :members:

.. autoclass:: globus_sdk.exc.TransferAPIError
   :members:

Auth High Level Interface
-------------------------

.. autoclass:: globus_sdk.AuthClient
   :members:

Nexus High Level Interface (DEPRECATED)
---------------------------------------

.. autoclass:: globus_sdk.NexusClient
   :members:

Responses
---------

.. autoclass:: globus_sdk.response.GlobusResponse
   :members:

.. autoclass:: globus_sdk.response.GlobusHTTPResponse
   :members:

Exceptions
----------

.. autoclass:: globus_sdk.exc.GlobusError
   :members:

.. autoclass:: globus_sdk.exc.GlobusAPIError
   :members:

.. autoclass:: globus_sdk.exc.PaginationOverrunError
   :members:
