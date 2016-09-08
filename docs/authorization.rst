.. _authorization:

API Authorization
=================

Authorizing calls against Globus can be a complex process.
In particular, if you are using Refresh Tokens and short-lived Access Tokens,
you may need to take particular care managing your Authorization state.

Within the SDK, we solve this problem by using :class:`GlobusAuthorizers
<globus_sdk.authorizers.base.GlobusAuthorizer>`, which are attached to clients.
These are a very simple class of generic objects which define a way of getting
an up-to-date ``Authorization`` header, and trying to handle a 401 (if that
header is expired).

You should be using :ref:`High-Level API <api>` and passing in an authorizer
whenever you create a new client.
The type of authorizer you will use depends very much on your application, but
if you want examples you should look at the :ref:`examples section
<examples-ref>`.
It may help to start with the examples and come back to the full documentation
afterwards.

.. _examples-ref:

Examples
--------

Using an authorizer is hard to grasp without a few examples to reference.
The basic usage should be to create these at client instantiation time.

Basic Auth on an AuthClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using an :class:`AuthClient <globus_sdk.AuthClient>` to do OAuth2
flows, you likely want to authenticate it using your client credentials (the
client ID and client secret).
Using the basic authorizer, it's as simple as

.. code-block:: python

    from globus_sdk import AuthClient, BasicAuthorizer

    CLIENT_ID = '...'
    CLIENT_SECRET = '...'

    # you probably want to give the client your CLIENT_ID as well, so that it
    # can use it for various OAuth2 operations
    client = AuthClient(client_type=AuthClient.CLIENT_TYPE_CONFIDENTIAL_APP,
                        client_id=CLIENT_ID,
                        authorizer=BasicAuthorizer(CLIENT_ID, CLIENT_SECRET))

and you're off to the races!

Access Token Authorization on AuthClient and TransferClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perhaps you're in a part of your application that only sees Access Tokens.
Access Tokens are used to directly authenticate calls against Globus APIs, and
are limited-lifetime credentials.
You have distinct Access Tokens for each Globus service which you want to
access.

With the tokens in hand, it's just as simple as the :class:`BasicAuthorizer
<globus_sdk.BasicAuthorizer>` case.

.. code-block:: python

    from globus_sdk import AuthClient, TransferClient, AccessTokenAuthorizer

    AUTH_ACCESS_TOKEN = '...'
    TRANSFER_ACCESS_TOKEN = '...'

    # note that we don't provide the client ID in this case
    # we aren't forbidden from doing so, but if you're using an Access Token
    # you can't do the OAuth2 flows
    # including it is allowed, but could be confusing since it won't be used
    auth_client = AuthClient(
        authorizer=AccessTokenAuthorizer(AUTH_ACCESS_TOKEN))

    transfer_client = TransferClient(
        authorizer=AccessTokenAuthorizer(TRANSFER_ACCESS_TOKEN))

Refresh Token Authorization on AuthClient and TransferClient
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refresh Tokens are long-lived credentials used to get new Access Tokens
whenever they expire.
However, it would be very awkward to create a new client instance every time
your credentials expire!
Instead, use a :class:`RefreshTokenAuthorizer
<globus_sdk.RefreshTokenAuthorizer>` to automatically re-up your credentials
whenever they near expiration.
Unfortunately, re-upping credentials is an operation that requires having
client credentials for Globus Auth, so creating the authorizer is more complex
this time.

.. code-block:: python

    from globus_sdk import (AuthClient, TransferClient, BasicAuthorizer,
                            RefreshTokenAuthorizer)

    # for doing the refresh
    CLIENT_ID = '...'
    CLIENT_SECRET = '...'

    # the actual tokens
    AUTH_REFRESH_TOKEN = '...'
    TRANSFER_REFRESH_TOKEN = '...'

    # making the authorizer requires that we have an AuthClient which can talk
    # OAuth2 to Globus Auth
    # note that this is 100% the same as doing basic auth above
    internal_auth_client = AuthClient(
        client_type=AuthClient.CLIENT_TYPE_CONFIDENTIAL_APP, client_id=CLIENT_ID,
        authorizer=BasicAuthorizer(CLIENT_ID, CLIENT_SECRET))

    # now let's bake a couple of authorizers
    auth_authorizer = RefreshTokenAuthorizer(AUTH_REFRESH_TOKEN,
                                             internal_auth_client)
    transfer_authorizer = RefreshTokenAuthorizer(TRANSFER_REFRESH_TOKEN,
                                                 internal_auth_client)

    # auth_client here is totally different from "internal_auth_client" above
    # the former is being used to request new tokens periodically, while this
    # one represents a user authenticated with those tokens
    auth_client = AuthClient(authorizer=auth_authorizer)
    # transfer_client doesn't have to contend with this duality -- it's always
    # representing a user
    transfer_client = TransferClient(authorizer=transfer_authorizer)

The Implicit Authorizers
~~~~~~~~~~~~~~~~~~~~~~~~

``AuthClient`` and ``TransferClient`` define a method of loading tokens from
the config files and creating an authorizer.

In the future, this will change to support refresh tokens in the config, but
today it is done with access tokens.

If you have a config file that reads as

.. code-block:: ini

    [general]
    auth_token = "abc123"
    transfer_token = "xyz456"

Then you can create ``AuthClient`` and ``TransferClient`` instances with no
arguments:

.. code-block:: python

    auth_client = AuthClient()
    transfer_client = TransferClient()

This is really just the same as doing this:

.. code-block:: python

    auth_client = AuthClient(
        authorizer=AccessTokenAuthorizer("abc123"))

    transfer_client = TransferClient(
        authorizer=AccessTokenAuthorizer("xyz456"))


The Authorizer Interface
------------------------

We define the interface for ``GlobusAuthorizer`` objects in terms of an
Abstract Base Class:

.. autoclass:: globus_sdk.authorizers.base.GlobusAuthorizer
    :members:
    :member-order: bysource

Authorizer Types
----------------

All of these types of authorizers can be imported from
``globus_sdk.authorizers``.

.. autoclass:: globus_sdk.BasicAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: globus_sdk.AccessTokenAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: globus_sdk.RefreshTokenAuthorizer
    :members: set_authorization_header, handle_missing_authorization
    :member-order: bysource
    :show-inheritance:
