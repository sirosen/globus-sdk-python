Changed
~~~~~~~

- The argument specification for ``AuthClient.create_policy`` was incorrect.
  The corrected method will emit deprecation warnings if called with positional
  arguments, as the corrected version uses keyword-only arguments. (:pr:`936`)
