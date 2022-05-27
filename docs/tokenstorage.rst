.. _tokenstorage:

TokenStorage
============

The TokenStorage component provides a way of storing and loading the tokens
received from authentication and token refreshes.

Usage
-----

TokenStorage is available under the name ``globus_sdk.tokenstorage``.

Storage adapters are the main objects of this subpackage. Primarily, usage
should revolve around creating a storage adapter, potentially loading data from
it, and using it as the ``on_refresh`` handler for an authorizer.

For example:

.. code-block:: python

    import os
    import globus_sdk
    from globus_sdk.tokenstorage import SimpleJSONFileAdapter

    my_file_adapter = SimpleJSONFileAdapter(os.path.expanduser("~/mytokens.json"))

    if not my_file_adapter.file_exists():
        # ... do a login flow, getting back initial tokens
        # elided for simplicity here
        token_response = ...
        # now store the tokens, and pull out the tokens for the
        # resource server we want
        my_file_adapter.store(token_response)
        by_rs = token_response.by_resource_server
        tokens = by_rs["transfer.api.globus.org"]
    else:
        # otherwise, we already did this whole song-and-dance, so just
        # load the tokens from that file
        tokens = my_file_adapter.get_token_data("transfer.api.globus.org")


    # RereshTokenAuthorizer and ClientCredentialsAuthorizer both use
    # `on_refresh` callbacks
    # this feature is therefore only relevant for those auth types
    #
    # auth_client is the internal auth client used for refreshes,
    # and which was used in the login flow
    # note that this is all normal authorizer usage wherein
    # my_file_adapter is providing the on_refresh callback
    auth_client = ...
    authorizer = globus_sdk.RefreshTokenAuthorizer(
        tokens["refresh_token"],
        auth_client,
        access_token=tokens["access_token"],
        expires_at=tokens["access_token_expires"],
        on_refresh=my_file_adapter.on_refresh,
    )

    # or, for client credentials
    authorizer = globus_sdk.ClientCredentialsAuthorizer(
        auth_client,
        ["urn:globus:auth:transfer.api.globus.org:all"],
        access_token=tokens["access_token"],
        expires_at=tokens["access_token_expires"],
        on_refresh=my_file_adapter.on_refresh,
    )

    # and then use the authorizer on a client!
    tc = globus_sdk.TransferClient(authorizer=authorizer)

Adapter Types
-------------

.. module:: globus_sdk.tokenstorage

``globus_sdk.tokenstorage`` provides base classes for building your own storage
adapters, and two complete adapters.

The :class:`SimpleJSONFileAdapter` is good for the "simplest possible" storage, using a
JSON file to store token data.

The :class:`SQLiteAdapter` is the next step up in complexity, for applications like the
globus-cli which need to store various tokens and additional configuration. In
addition to basic token storage, the :class:`SQLiteAdapter` provides for namespacing
of the token data, and for additional configuration storage.

Reference
---------

.. autoclass:: StorageAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: FileAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: SimpleJSONFileAdapter
   :members:
   :member-order: bysource
   :show-inheritance:

.. autoclass:: SQLiteAdapter
   :members:
   :member-order: bysource
   :show-inheritance:
