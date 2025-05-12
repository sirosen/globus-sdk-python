Removed
~~~~~~~

- The SDK no longer sets default scopes for direct use of client
  credentials and auth client login flow methods. Users should either use
  ``GlobusApp`` objects, which can specify scopes based on the clients in use,
  or else pass a list of scopes explicitly to
  ``oauth2_client_credentials_tokens`` or ``oauth2_start_flow``. (:pr:`1186`)
