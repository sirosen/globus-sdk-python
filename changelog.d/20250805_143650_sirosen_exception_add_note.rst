Added
-----

- On Python 3.11+, the SDK will populate the ``__notes__`` of API errors with a
  message containing the full body of the error response.
  ``__notes__`` is part of the default presentation of a traceback. (:pr:`1299`)
