* Enhance scope utilities with scope parsing, attached to
  ``globus_sdk.scopes.Scope`` (:pr:`NUMBER`)

  * ``MutableScope`` has been renamed to ``Scope``. Both names remain available
    for backwards compatibility, but the preferred name is now ``Scope``

  * ``Scope.parse`` and ``Scope.deserialize`` can now be used to parse strings
    into ``Scope``\s
