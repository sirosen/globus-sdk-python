.. _example_token_storage:

Token Storage objects
=====================

DynamoDB Token Storage
----------------------

The following example demonstrates a token storage which uses AWS DynamoDB as
the backend storage mechanism.

Unlike the builtin storage interfaces for JSON and sqlite, enumerating tokens in
a DyanmoDB table-backed storage is not a desirable operation.
DynamoDB functions as a key-value store, and can efficiently map keys,
but features slow sequential scans for enumeration.

The example implements sequential scans but also prints a noisy warning when
that activity is triggered. An alternative implementation could raise an error
and refuse to execute the scan.

.. caution::

    Raising errors on calls to get the full suite of tokens will work for many
    use cases, but it is required by the interface so that SDK features can rely
    on it being present.

    Some capabilities, like ``GlobusApp.logout(sweep=True)`` call this method
    and will fail if it is not implemented.

.. literalinclude:: dynamodb_token_storage.py
    :caption: ``dynamodb_token_storage.py`` [:download:`download <dynamodb_token_storage.py>`]
    :language: python
