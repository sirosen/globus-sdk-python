.. _example_minimal_transfer:

File Transfer Scripts
=====================

Minimal File Transfer Script
----------------------------

The following is an extremely minimal script to demonstrate a file transfer
using the :class:`TransferClient <globus_sdk.TransferClient>`.

It uses the tutorial client ID from the :ref:`tutorials <tutorials>`.

.. note::
    You will need to replace the values for ``source_collection_id`` and
    ``dest_collection_id`` with UUIDs of collections that you have access to.

.. literalinclude:: transfer_minimal.py
    :caption: ``transfer_minimal.py`` [:download:`download <transfer_minimal.py>`]
    :language: python

Best-Effort Proactive Handling of ConsentRequired
-------------------------------------------------

The above example works in most cases, and especially when there is a low cost
to failing and retrying an activity. The ``auto_redrive_gares`` flag enables a
behavior which will prompt the user for a fresh login if they are missing
consents for access to various collections.

However, in some cases, responding to missing consents when the task is
submitted is not acceptable. For example, for scripts used in batch job systems,
the user cannot respond to the error until the job is already executing. The
user would rather handle such issues when submitting their job.

The service still relies on ``ConsentRequired`` errors to indicate that some
additional user consent is needed. But we can intentionally trigger them early
to control when the user is prompted to resolve them.

The example below tries an ``ls`` operation before starting to build the task
data. If the ``ls`` fails with ``ConsentRequired``, the user can be put through
the relevant login flow. Other errors (e.g., bad permissions) are suppressed, as
they probably aren't relevant to the user.

.. note::
    The ``UserApp`` object is instantiated a second time, later in the script, to
    actually start the transfer. This loads the same tokens from the earlier login
    via the default token storage in ``~/.globus/``.

    To manage tokens in another way, please see the documentation on
    :ref:`Token Storages <token_storages>`.

.. literalinclude:: transfer_consent_required_proactive.py
    :caption: ``transfer_consent_required_proactive.py`` [:download:`download <transfer_consent_required_proactive.py>`]
    :language: python
