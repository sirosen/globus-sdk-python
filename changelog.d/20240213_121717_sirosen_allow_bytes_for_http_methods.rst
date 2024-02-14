Added
~~~~~

- All of the basic HTTP methods of ``BaseClient`` and its derived classes which
  accept a ``data`` parameter for a request body, e.g. ``TransferClient.post``
  or ``GroupsClient.put``, now allow the ``data`` to be passed in the form of
  already encoded ``bytes``. (:pr:`951`)
