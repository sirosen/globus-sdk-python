* Error parsing in the SDK has been enhanced to better support JSON:API and
  related error formats with multiple sub-errors. Several attributes are
  added or changed. (:pr:`NUMBER`)

  * A new attribute is added to API error objects, ``errors``. This is a list
    of subdocuments parsed from the error data, especially relevant for
    JSON:API errors and similar formats.

  * A new attribute is now present on API error objects, ``messages``. This is
    a list of messages parsed from the error data, for errors with multiple
    messages. When there is only one message, ``messages`` will only contain
    one item.

  * The ``message`` field is now an alias for a joined string of
    ``messages``. Assigning a string to ``message`` is supported for error
    subclasses, but is deprecated.

  * ``message`` will now be ``None`` when no messages can be parsed from the error data.
    Previously, the default for ``message`` would be an alias for ``text``.

  * An additional field is checked by default for error message data,
    ``title``. This is useful when JSON:API errors contain ``title`` but no
    ``detail`` field.

  * The ``code`` field of errors will no longer attempt to parse only the first
    ``code`` from multiple sub-errors. Instead, ``code`` will first parse a
    top-level ``code`` field, and then fallback to checking if *all* sub-errors
    have the same ``code`` value. The result is that certain errors which would
    populate a non-default ``code`` value no longer will, but the ``code`` will
    also no longer be misleading when multiple errors with different codes are
    present in an error object.

* Behavior has changed slightly specifically for ``TimerAPIError``. When parsing
  fails, the ``code`` will be ``Error`` and the ``messages`` will be empty.
