* Add helper objects and methods for interacting with Globus Connect Server
  Storage Gateways (:pr:`554`)

  * New methods on ``GCSClient``: ``create_storage_gateway``, ``get_storage_gateway``,
    ``get_storage_gateway_list``, ``update_storage_gateway``,
    ``delete_storage_gateway``

  * New helper classes for constructing storage gateway documents.
    ``StorageGatewayDocument`` is the main one, but also
    ``POSIXStoragePolicies`` and ``POSIXStagingStoragePolicies`` are added for
    declaring the storage gateway ``policies`` field. More policy helpers will
    be added in future versions.
