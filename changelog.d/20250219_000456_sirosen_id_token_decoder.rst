Added
~~~~~

- Introduce ``globus_sdk.IDTokenDecoder``, which implements ``id_token``
  decoding. (:pr:`1136`)

  - For integration with ``GlobusApp``, a new builder protocol is defined,
    ``IDTokenDecoderProvider``. This defines instantiation within the context
    of an app.

  - When ``OAuthTokenResponse.decode_id_token`` is called, it now internally
    instantiates an ``IDTokenDecoder`` and uses it to perform the decode.

  - ``IDTokenDecoder`` objects cache OpenID configuration data and JWKs
    after looking them up. If a decoder is used multiple times, it will reuse
    the cached data.

  - Token storage constructs can now contain an ``IDTokenDecoder`` in their
    ``id_token_decoder`` attribute. The decoder is used preferentially when
    trying to read the ``sub`` field from an ``id_token`` to store.

  - ``GlobusAppConfig`` can now contain ``id_token_decoder``, an
    ``IDTokenDecoder`` or ``IDTokenDecoderProvider``.
    The default is ``IDTokenDecoder``.

  - ``GlobusApp`` initialization will now use the config's
    ``id_token_decoder`` and attach the ``IDTokenDecoder`` to the
    token storage which is used.
