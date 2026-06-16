Fixed
-----

- Fix a crash bug in the orjson compatibility module. (:pr:`1396`)

  This manifested as a ``RuntimeError``, and could occur when a test framework
  accessed the module to check for warning registries in the module.
