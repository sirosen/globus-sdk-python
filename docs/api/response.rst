Responses
=========

All method return values for Globus SDK Clients are ``GlobusResponse``
objects or a simple data structure (typically a Python list or other
iterable) containing ``GlobusResponse`` objects.

To customize client methods with additional detail, we may use subclasses of
``GlobusResponse``.
For example the ``GlobusHTTPResponse`` attaches HTTP response information.

Response Classes
----------------

.. autoclass:: globus_sdk.response.GlobusResponse
   :members:

.. autoclass:: globus_sdk.response.GlobusHTTPResponse
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: globus_sdk.transfer.response.TransferResponse
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: globus_sdk.transfer.response.IterableTransferResponse
   :members:
   :inherited-members:
   :show-inheritance:
