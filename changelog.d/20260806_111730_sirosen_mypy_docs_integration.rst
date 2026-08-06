Added
-----

- Added a new flag, ``sweep``, to ``GlobusApp.logout()``.
  Use ``logout(sweep=True)`` to ask the app to clear all tokens found in the
  app's storage, not only the ones currently in use by the app.
  The default behavior, ``sweep=False``, is unchanged. (:pr:`NUMBER`)
