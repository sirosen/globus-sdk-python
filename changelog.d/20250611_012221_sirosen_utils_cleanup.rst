Changed
~~~~~~~

- Payload types now inherit from ``dict`` rather than ``UserDict``. The
  ``PayloadWrapper`` utility class has been replaced with ``Payload``. (:pr:`NUMBER`)
- Payload types are more consistent about encoding missing values using ``MISSING``. (:pr:`NUMBER`)
