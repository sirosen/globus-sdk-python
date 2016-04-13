.. _api:

High Level API
==============

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

    print("My Last 25 Tasks:")
    # `filter` to get Delete Tasks (default is just Transfer Tasks)
    for task in tc.task_list(num_results=25, filter="type:TRANSFER,DELETE"):
        print(task["task_id"], task["type"], task["status"])


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
