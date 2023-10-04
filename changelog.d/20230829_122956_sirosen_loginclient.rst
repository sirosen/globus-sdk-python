Changed
~~~~~~~

- The inheritance structure used for Globus Auth client classes has changed.
  (:pr:`NUMBER`)

  - A new class, ``AuthLoginClient``, is the base for ``NativeAppAuthClient``
    and ``ConfidentialAppAuthClient``. These classes no longer inherit from
    ``AuthClient``.

  - ``AuthClient`` is now the only class which provides functionality
    for accessing Globus Auth APIs. Previously, some of the API accessing
    methods were inherited by the ``AuthClient`` subclasses, but would never
    work.

Deprecated
~~~~~~~~~~

- Several features of Auth client classes are now deprecated. (:pr:`NUMBER`)

  - Setting ``AuthClient.client_id`` or accessing it as an attribute
    is deprecated and will emit a warning.

  - ``ConfidentialAppAuthClient.get_identities`` has been preserved as a valid
    call, but will emit a warning. Users wishing to access this API via client
    credentials should prefer to get an access token using a client credential
    callout, and then use that token to call ``AuthClient.get_identities()``.
