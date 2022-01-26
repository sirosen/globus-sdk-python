Globus Search
=============

.. autoclass:: globus_sdk.SearchClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

Note that you should not use ``SearchQueryBase`` directly, and it is not
importable from the top level of the SDK. It is included in documentation
only to document the methods it provides to its subclasses.

.. autoclass:: globus_sdk.services.search.data.SearchQueryBase
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.SearchQuery
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.SearchScrollQuery
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a ``SearchClient`` will raise this specialized type of
error, rather than a generic ``GlobusAPIError``.

.. autoclass:: globus_sdk.SearchAPIError
   :members:
   :show-inheritance:
