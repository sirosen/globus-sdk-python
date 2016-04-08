.. _api:

Developer Interface
===================

.. module:: globus_sdk

Common Low Level Interface
--------------------------

All service clients support the low level interface, provides by the
BaseClient.

.. autoclass:: globus_sdk.base.BaseClient
   :members: get, put, post, delete, set_token, set_auth_basic, set_app_name

Transfer High Level Interface
-----------------------------

.. autoclass:: globus_sdk.TransferClient
   :members:
   :inherited-members:
   :show-inheritance:
   :exclude-members: error_class, response_class

.. autoclass:: globus_sdk.exc.TransferAPIError
   :members:
   :show-inheritance:

Auth High Level Interface
-------------------------

.. autoclass:: globus_sdk.AuthClient
   :members:
   :inherited-members:
   :show-inheritance:
   :exclude-members: error_class, response_class

Responses
---------

.. autoclass:: globus_sdk.response.GlobusResponse
   :members:

.. autoclass:: globus_sdk.response.GlobusHTTPResponse
   :members:
   :inherited-members:
   :show-inheritance:

Exceptions
----------

.. autoclass:: globus_sdk.exc.GlobusError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.GlobusAPIError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.PaginationOverrunError
   :members:
   :show-inheritance:
