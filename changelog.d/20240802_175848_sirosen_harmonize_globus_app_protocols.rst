Changed
~~~~~~~

- The experimental ``TokenStorageProvider`` and ``LoginFlowManagerProvider``
  protocols have been updated to require keyword-only arguments for their
  ``for_globus_app`` methods. This protects against potential ordering
  confusion for their arguments. (:pr:`1028`)
