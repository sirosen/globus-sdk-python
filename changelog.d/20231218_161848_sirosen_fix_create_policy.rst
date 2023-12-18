Changed
~~~~~~~

- The argument specification for ``AuthClient.create_policy`` was incorrect.
  Fixing this required a breaking change to the signature, and all arguments
  to that method are now specified as keyword-only. (:pr:`NUMBER`)
