Added
~~~~~

- A new sentinel value, ``globus_sdk.MISSING``, has been introduced.
  It is used for method calls which need to distinguish missing parameters from
  an explicit ``None`` used to signify ``null`` (:pr:`885`)

  - ``globus_sdk.MISSING`` is now supported in payload data for all methods, and
    will be automatically removed from the payload before sending to the server
