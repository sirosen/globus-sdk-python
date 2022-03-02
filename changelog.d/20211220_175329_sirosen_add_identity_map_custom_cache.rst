* ``globus_sdk.IdentityMap`` can now take a cache as an input. This allows
  multiple ``IdentityMap`` instances to share the same storage cache. Any
  mutable mapping type is valid, so the cache can be backed by a database or
  other storage (:pr:`NUMBER`)
