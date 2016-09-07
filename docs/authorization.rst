Globus Authorization
====================

Authorizing calls against Globus can be a complex process.
In particular, if you are using Refresh Tokens and short-lived Access Tokens,
you may need to take particular care managing your Authorization state.

Within the SDK, we solve this problem by using :class:`GlobusAuthorizers
<globus_sdk.authorizers.GlobusAuthorizer>`.
These are a very simple class of generic objects which define a way of getting
an up-to-date ``Authorization`` header, and trying to handle a 401 (if that
header is expired).

Unless you are using Refresh Tokens, you should just use the
`High-Level API <_api>`_ and rely on that to create a ``GlobusAuthorizer`` for
you whenever one is necessary.

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
