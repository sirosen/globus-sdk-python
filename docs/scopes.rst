Scopes and ScopeBuilders
========================

OAuth2 Scopes for various Globus services are represented by ``ScopeBuilder``
objects.

A number of pre-set scope builders are provided and populated with useful data,
and they are also accessible via the relevant client classes.

Direct Use (as constants)
-------------------------

To use the scope builders directly, import from ``globus_sdk.scopes``.

For example, one might use the Transfer "all" scope during a login flow like
so:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[TransferScopes.all])
    ...

As Client Class Attributes
--------------------------

Because the scopes for a token are associated with some concrete client which
will use that token, it makes sense to associate a scope with a client class.

The Globus SDK does this by providing the ``ScopeBuilder`` for a service as an
attribute of the client. For example,

.. code-block:: python

    import globus_sdk

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[globus_sdk.TransferClient.scopes.all])
    ...

    # or, potentially, after there is a concrete client
    _tc = globus_sdk.TransferClient()
    client.oauth2_start_flow(requested_scopes=[_tc.scopes.all])

Using a Scope Builder to Get Matching Tokens
--------------------------------------------

A ``ScopeBuilder`` contains the resource server name used to get token data
from a token response.
To elaborate on the above example:

.. code-block:: python

    import globus_sdk
    from globus_sdk.scopes import TransferScopes

    CLIENT_ID = "<YOUR_ID_HERE>"

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(requested_scopes=[TransferScopes.all])
    authorize_url = client.oauth2_get_authorize_url()
    print("Please go to this URL and login:", authorize_url)
    auth_code = input("Please enter the code you get after login here: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # use the `resource_server` of a ScopeBuilder to grab the associated token
    # data from the response
    tokendata = token_response.by_resource_server[TransferScopes.resource_server]

ScopeBuilder Types and Constants
--------------------------------

.. autoclass:: globus_sdk.scopes.ScopeBuilder
    :members:
    :show-inheritance:

.. autoclass:: globus_sdk.scopes.GCSScopeBuilder
    :members:
    :show-inheritance:

.. autodata:: globus_sdk.scopes.AuthScopes
    :annotation:

.. autodata:: globus_sdk.scopes.GroupsScopes
    :annotation:

.. autodata:: globus_sdk.scopes.NexusScopes
    :annotation:

.. autodata:: globus_sdk.scopes.SearchScopes
    :annotation:

.. autodata:: globus_sdk.scopes.TransferScopes
    :annotation:
