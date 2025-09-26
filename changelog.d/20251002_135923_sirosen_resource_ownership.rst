Added
-----

- ``GlobusApp`` usages now support resource tracking in which they will close
  the transports used by registered clients and the underlying token storage
  when via a ``close()`` method. (:pr:`NUMBER`)

  - ``GlobusApp`` now features a ``close()`` method for doing imperative
    resource cleanup.

  - ``GlobusApp`` can be used as a context manager, and calls ``close()`` on
    exit.

  - Transports which are created by clients, and token storages which
    are created by apps, are subject to this cleanup behavior. Imperatively
    created ones which are passed in to clients and apps are not.

  - The SDK internally tracks the relationships between apps, clients,
    transports, and token storages for these purposes.
    `Weak references <docs.python.org/3/library/weakref.html>`_ are used to
    minimize the impact of resource tracking on garbage collection.
