* Several improvements to Transfer helper objects (:pr:`573`)

  * Add ``TransferData.add_filter_rule`` for adding filter rules (exclude
    rules) to transfers
  * Add ``skip_activation_check`` as an argument to ``DeleteData`` and
    ``TransferData``
  * The ``sync_level`` argument to ``TransferData`` is now annotated more
    accurately to reject bad strings
