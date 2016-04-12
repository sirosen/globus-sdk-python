.. _api:

Developer Interface
===================

The Globus SDK provides a client class for every public Globus API.
Each client object can take authentication credentials from config files,
environment variables, or programmatically (either as a parameter at
instantiation time, or as a modification after the fact).
Once instantiated, a Client gives you high-level interface to make API calls,
without needing to know Globus API endpoints or their various parameters.

For example, you could use the ``TransferClient`` to list your task history
very simply::

    from globus_sdk import TransferClient

    tc = TransferClient() # uses transfer_token from the config file

    print('My Last 25 Tasks:')
    # `filter` to get Delete Tasks (default is just Transfer Tasks)
    for task in tc.task_list(num_results=25, filter='type:TRANSFER,DELETE'):
        print(task.data['task_id'], task.data['type'], task.data['status'])


.. module:: globus_sdk

Transfer Client
---------------

.. autoclass:: globus_sdk.TransferClient
   :members:
   :member-order: bysource
   :inherited-members:
   :show-inheritance:
   :exclude-members: error_class, response_class

.. autoclass:: globus_sdk.exc.TransferAPIError
   :members:
   :show-inheritance:

Auth Client
-----------

.. autoclass:: globus_sdk.AuthClient
   :members:
   :member-order: bysource
   :inherited-members:
   :show-inheritance:
   :exclude-members: error_class, response_class

Common Low Level Interface
--------------------------

All service clients support the low level interface, provided by the
``BaseClient``.

.. autoclass:: globus_sdk.base.BaseClient
   :members: get, put, post, delete, set_token, set_auth_basic, set_app_name
   :member-order: bysource

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
