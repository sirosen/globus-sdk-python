Changed
~~~~~~~

- The inheritance structure used for Globus Auth client classes has changed.
  (:pr:`NUMBER`)

  - A new class, ``AuthLoginClient``, is the base for ``NativeAppAuthClient``
    and ``ConfidentialAppAuthClient``. These classes no longer inherit from
    ``AuthClient``.

  - ``AuthClient`` is now an alias for ``AuthServiceClient``. The new name is
    preferred but the old name is not yet deprecated.

  - ``AuthServiceClient`` is now the only class which provides functionality
    for accessing Globus Auth APIs. Previously, some of the API accessing
    methods were inherited by the ``AuthClient`` subclasses, but would never
    work.

  - All of these client classes descend from a common base, ``AuthBaseClient``.
    Users should not instantiate this class directly, but it provides
    common functionality for all clients to Globus Auth.

Deprecated
~~~~~~~~~~

- Several features of Auth client classes are now deprecated. (:pr:`NUMBER`)

  - Setting ``AuthServiceClient.client_id`` or accessing it as an attribute
    is deprecated and will emit a warning. ``AuthClient`` is now an alias for
    ``AuthServiceClient``, so this applies to both names.

  - ``ConfidentialAppAuthClient.get_identities`` has been preserved as a valid
    call, but will emit a warning. Users wishing to access this API via client
    credentials should prefer to get an access token using a client credential
    callout, and then use that token to call ``get_identities`` using an
    ``AuthServiceClient``.
