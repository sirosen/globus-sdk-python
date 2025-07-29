Globus Search
=============

.. currentmodule:: globus_sdk

.. autoclass:: SearchClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

.. autoclass:: SearchQueryV1
    :members:
    :show-inheritance:

.. autoclass:: SearchScrollQuery
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`SearchClient` will raise this specialized type of
error, rather than a generic :class:`GlobusAPIError`.

.. autoclass:: SearchAPIError
   :members:
   :show-inheritance:
