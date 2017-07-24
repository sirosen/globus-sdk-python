Transfer Responses
==================

.. automodule:: globus_sdk.transfer.response
   :members:
   :show-inheritance:


PaginatedResource Responses
---------------------------

The ``PaginatedResource`` class should not typically be instantiated directly,
but is returned from several :class:`TransferClient
<globus_sdk.transfer.client.TransferClient>` methods.
It is an iterable of ``GlobusRepsonse`` objects.


.. autoclass:: globus_sdk.transfer.paging.PaginatedResource
   :members: data
   :show-inheritance:
