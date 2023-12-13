Changed
~~~~~~~

- Minor improvements to handling of paths and URLs. (:pr:`NUMBER`)

  - Request paths which start with the ``base_path`` of a client are now
    normalized to avoid duplicating the ``base_path``.

  - When a ``GCSClient`` is initialized with an HTTPS URL, if the URL does not
    end with the ``/api`` suffix, that suffix will automatically be appended.
    This allows the ``gcs_manager_url`` field from Globus Transfer to be used
    verbatim as the address for a ``GCSClient``.
