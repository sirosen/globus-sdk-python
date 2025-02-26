Added
~~~~~

- Introduce ``globus_sdk.IDTokenDecoder`` and
  ``globus_sdk.JWTDecoder`` classes, which implement ``id_token``
  decoding. (:pr:`NUMBER`)

  - ``JWTDecoder`` is an abstract class declaring the interface, while
    ``IDTokenDecoder`` is the primary implementation.

  - For integration with ``GlobusApp``, a new builder protocol is defined,
    ``JWTDecoderProvider``. This defines instantiation within the context of an
    app. ``IDTokenDecoder`` implements ``JWTDecoderProvider``.

  - These new classes define how OIDC ``id_token``\s should be decoded. When
    ``OAuthTokenResponse.decode_id_token`` is called, it now internally
    instantiates an ``IDTokenDecoder`` and uses it to perform the decode.

  - ``IDTokenDecoder`` objects cache OpenID configuration data and JWKs
    after looking them up. If a decoder is used multiple times, it will reuse
    the cached data.

  - Token storage constructs can now contain a ``JWTDecoder`` in their
    ``id_token_decoder`` attribute. The decoder is used preferentially when
    trying to read the ``sub`` field from an ``id_token`` to store.

  - ``GlobusAppConfig`` can now contain ``id_token_decoder``, a ``JWTDecoder``
    or ``JWTDecoderProvider``. The default is ``IDTokenDecoder``.

  - ``GlobusApp`` initialization will now use the config's
    ``id_token_decoder`` and attach the ``JWTDecoder`` to the
    token storage which is used.
