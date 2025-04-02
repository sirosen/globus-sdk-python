Changed
~~~~~~~

- The initialization of a client with a ``GlobusApp`` has been improved and is
  now available under the public ``attach_globus_app`` method on client
  classes. Attaching an app is only valid for clients which were initialized
  without an app or authorizer. (:pr:`1137`)

- When a ``GlobusApp`` is used with a client, that client's ``app_scopes``
  attribute will now always be populated with the scopes that it passed back to
  the app. (:pr:`1137`)
