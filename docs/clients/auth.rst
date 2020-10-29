.. module:: globus_sdk.auth

Globus Auth
===========

There are several types of client object for communicating with the Globus Auth
service. A client object may represent your application (as the driver of
authentication and authorization flows), in which case the
``NativeAppAuthClient`` or ``ConfidentialAppAuthClient`` classes should
generally be used.

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

The ``IdentityMap`` is a specialized object which aids in the particular
use-case in which the Globus Auth ``get_identities`` API is being used to
resolve large numbers of usernames or IDs. It combines caching, request
batching, and other functionality.

..
    We set special-members so that __getitem__ and __delitem__ are included.
    But then we need to exclude specific members because we don't want people
    reading about __weakref__ in our docs.
.. autoclass:: globus_sdk.IdentityMap
   :members:
   :special-members:
   :exclude-members: __dict__,__weakref__
   :show-inheritance:

Auth Responses
--------------

.. autoclass:: globus_sdk.auth.token_response.OAuthTokenResponse
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.auth.token_response.OAuthDependentTokenResponse
   :members:
   :show-inheritance:

OAuth2 Flows & Explanation
--------------------------

.. toctree::
   auth/oauth2
   auth/oauth2_flows
   auth/resource_servers
