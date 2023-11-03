Added
~~~~~

.. note::
    These changes pertain to methods of the client objects in the SDK which
    interact with Globus Auth client registration.
    To disambiguate, we refer to the Globus Auth entities below as "Globus Auth
    clients" or specify "in Globus Auth", as appropriate.

- Globus Auth clients objects now have methods for interacting with client and
  project APIs. (:pr:`884`)

  - ``NativeAppAuthClient.create_native_app_instance`` creates a new native app
    instance in Globus Auth for a client.

  - ``ConfidentialAppAuthClient.create_child_client`` creates a child client in
    Globus Auth for a confidential app.

  - ``AuthClient.get_project`` looks up a project.

  - ``AuthClient.get_policy`` looks up a policy document.

  - ``AuthClient.get_policies`` lists all policies in all projects for which
    the current user is an admin.

  - ``AuthClient.create_policy`` creates a new policy.

  - ``AuthClient.update_policy`` updates an existing policy.

  - ``AuthClient.delete_policy`` deletes a policy.

  - ``AuthClient.get_client`` looks up a Globus Auth client by ID or FQDN.

  - ``AuthClient.get_clients`` lists all Globus Auth clients for which the
    current user is an admin.

  - ``AuthClient.create_client`` creates a new client in Globus Auth.

  - ``AuthClient.update_client`` updates an existing client in Globus Auth.

  - ``AuthClient.delete_client`` deletes a client in Globus Auth.

  - ``AuthClient.get_client_credentials`` lists all client credentials for a
    given Globus Auth client.

  - ``AuthClient.create_client_credential`` creates a new client credential for
    a given Globus Auth client.

  - ``AuthClient.delete_client_credential`` deletes a client credential.

  - ``AuthClient.get_scope`` looks up a scope.

  - ``AuthClient.get_scopes`` lists all scopes in all projects for which the
    current user is an admin.

  - ``AuthClient.create_scope`` creates a new scope.

  - ``AuthClient.update_scope`` updates an existing scope.

  - ``AuthClient.delete_scope`` deletes a scope.

- A helper object has been defined for dependent scope manipulation via the
  scopes APIs, ``globus_sdk.DependentScopeSpec`` (:pr:`884`)
