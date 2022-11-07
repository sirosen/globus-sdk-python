* When ``GlobusHTTPResponse`` contains a list, calls to ``get()`` will no
  longer fail with an ``AttributeError`` but will return the default value
  (``None`` if unspecified) instead (:pr:`644`)
