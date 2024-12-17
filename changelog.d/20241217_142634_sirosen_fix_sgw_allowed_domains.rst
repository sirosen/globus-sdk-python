Fixed
~~~~~

- Fix a bug in ``StorageGatewayDocument`` which stored any ``allowed_domains``
  argument under an ``"allow_domains"`` key instead of the correct key,
  ``"allowed_domains"``. (:pr:`NUMBER`)
