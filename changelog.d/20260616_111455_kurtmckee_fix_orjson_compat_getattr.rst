Fixed
-----

- Fix a crash bug in the orjson compatibility module. (:pr:`NUMBER`)

  This manifested as a ``RuntimeError``, and could occur when a test framework
  accessed the module to check for warning registries in the module.
