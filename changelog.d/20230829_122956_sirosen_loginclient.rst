Changed
~~~~~~~

- The inheritance structure used for Globus Auth client classes has changed.
  (:pr:`849`)

  - A new class, ``AuthLoginClient``, is the base for ``NativeAppAuthClient``
    and ``ConfidentialAppAuthClient``. These classes no longer inherit from
    ``AuthClient``, and therefore no longer inherit certain methods which would
    never succeed if called.

  - ``AuthClient`` is now the only class which provides functionality
    for accessing Globus Auth APIs.

  - ``AuthClient`` no longer includes methods for OAuth 2 login flows which
    would only be valid to call on ``AuthLoginClient`` subclasses.

Deprecated
~~~~~~~~~~

- Several features of Auth client classes are now deprecated. (:pr:`849`)

  - Setting ``AuthClient.client_id`` or accessing it as an attribute
    is deprecated and will emit a warning.

  - ``ConfidentialAppAuthClient.get_identities`` has been preserved as a valid
    call, but will emit a warning. Users wishing to access this API via client
    credentials should prefer to get an access token using a client credential
    callout, and then use that token to call ``AuthClient.get_identities()``.
