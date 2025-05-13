Breaking Changes
~~~~~~~~~~~~~~~~

- The default for ``GlobusAPIError.code`` is now ``None``, when no ``code`` is
  supplied in the error body. It previously was ``"Error"``. (:pr:`NUMBER`)
