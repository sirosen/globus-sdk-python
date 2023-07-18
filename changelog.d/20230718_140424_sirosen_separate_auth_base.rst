Changed
~~~~~~~

- The inheritance hierarchy for Globus Auth client classes has changed. (:pr:`NUMBER`)

  - A new class, ``BaseAuthClient`` is used as the base for the other three
    existing Globus Auth clients

  - ``NativeAppAuthClient`` and ``ConfidentialAppAuthClient`` inherit from
    ``BaseAuthClient``, not ``AuthClient``

  - ``NativeAppAuthClient`` and ``ConfidentialAppAuthClient`` have lost methods
    which would never work in practice for these client types, e.g.
    ``create_project``
