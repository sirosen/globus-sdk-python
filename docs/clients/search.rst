.. module:: globus_sdk.search


Search Client (BETA)
====================

The SearchClient interface is in Beta, but the Search API is a fully
supported, production service.
Its docs are visible here: https://docs.globus.org/api/search/


.. autoclass:: globus_sdk.SearchClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class, default_response_class

Helper Objects
--------------

.. autoclass:: globus_sdk.SearchQuery
   :members:
   :show-inheritance:

Specialized Errors
------------------

.. autoclass:: globus_sdk.exc.SearchAPIError
   :members:
   :show-inheritance:
