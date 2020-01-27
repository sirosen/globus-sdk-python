.. module:: globus_sdk.auth

Auth Client
===========

.. autoclass:: globus_sdk.AuthClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class, default_response_class

.. autoclass:: globus_sdk.NativeAppAuthClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class, default_response_class

.. autoclass:: globus_sdk.ConfidentialAppAuthClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class, default_response_class

Helper Objects
--------------

..
    We set special-members so that __getitem__ and __delitem__ are included.
    But then we need to exclude specific members because we don't want people
    reading about __weakref__ in our docs.
.. autoclass:: globus_sdk.IdentityMap
   :members:
   :special-members:
   :exclude-members: __dict__,__weakref__
   :show-inheritance:
