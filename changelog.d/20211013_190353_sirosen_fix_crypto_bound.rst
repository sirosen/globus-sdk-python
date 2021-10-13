* Adjust package metadata for `cryptography` dependency, specifying
  `cryptography>=3.3.1` and no upper bound. This is meant to help mitigate
  issues in which an older `cryptography` version is installed gets used in
  spite of it being incompatible with `pyjwt[crypto]>=2.0` (:pr:`NUMBER`)
