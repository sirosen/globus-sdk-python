* Several minor bugs have been found and fixed (:pr:`504`)
** Exceptions raised in the SDK always use ``raise ... from`` syntax where
   appropriate. This corrects exception chaining in the local endpoint and
   several response objects.
** The encoding of files opened by the SDK is now always ``UTF-8``
** ``TransferData`` will now reject unsupported ``sync_level`` values with a
   ``ValueError`` on initialization, rather than erroring at submission time.
   The ``sync_level`` has also had its type annotation fixed to allow for
   ``int`` values.
** Several instances of undocumented parameters have been discovered, and these
   are now rectified.
