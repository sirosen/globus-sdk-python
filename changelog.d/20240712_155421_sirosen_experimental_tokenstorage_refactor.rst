Changed
~~~~~~~

- The ``SQLiteTokenStorage`` component in ``globus_sdk.experimental`` has been
  changed in several ways to improve its interface. (:pr:`1004`)

  - ``:memory:`` is no longer accepted as a database name. Attempts to use it
    will trigger errors directing users to use ``MemoryTokenStorage`` instead.

  - Parent directories for a target file are automatically created, and this
    behavior is inherited from the ``FileTokenStorage`` base class. (This was
    previously a feature only of the ``JSONTokenStorage``.)

  - The ``config_storage`` table has been removed from the generated database
    schema, the schema version number has been incremented to ``2``, and
    methods and parameters related to manipulation of ``config_storage`` have
    been removed.
