Added
~~~~~

- Introduce ``globus_sdk.IDTokenDecoder`` and
  ``globus_sdk.DefaultIDTokenDecoder`` classes, which implement ``id_token``
  decoding. (:pr:`NUMBER`)

  - These new classes define how OIDC ``id_token``\s should be decoded. When
    ``OAuthTokenResponse.decode_id_token`` is called, it now internally
    instantiates a ``DefaultIDTokenDecoder`` and uses it to perform the decode.

  - ``DefaultIDTokenDecoder`` objects cache OpenID configuration data and JWKs
    after looking them up. If a decoder is used multiple times, it will reuse
    the cached data.

  - Token storage constructs can now contain an ``IDTokenDecoder`` in their
    ``id_token_decoder`` attribute. The decoder is used preferentially when
    trying to read the ``sub`` field from an ``id_token`` to store.

  - ``GlobusAppConfig`` can now contain an ``IDTokenDecoder``, which will be
    attached to the underlying token storage during app initialization.

  - ``GlobusApp`` initialization will now attach an ``IDTokenDecoder`` to the
    token storage which is used. If no ``IDTokenDecoder`` was provided via
    the ``config``, a new ``DefaultIDTokenDecoder`` is used for this purpose.
