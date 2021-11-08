* A new experimental `mypy` plugin is now provided by the SDK under the name
  `globus_sdk._mypy_ext`. This plugin is able to recognize and rewrite the
  types on paginated methods like `TransferClient.paginated.endpoint_search` in
  order to correctly specify the types of paginated method arguments (:pr:`NUMBER`)
