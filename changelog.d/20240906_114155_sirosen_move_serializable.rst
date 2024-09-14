Added
~~~~~

- ``globus_sdk.exc.ValidationError`` is a new error type used by the SDK for
  certain cases of ``ValueError``\s which are caused by invalid content. It can
  also be accessed as ``globus_sdk.ValidationError``. (:pr:`NUMBER`)

Changed
~~~~~~~

- Imports of ``globus_sdk.exc`` now defer importing ``requests`` so as to
  reduce import-time performance impact the library is not needed. (:pr:`NUMBER`)

  The following error classes are now lazily loaded even when
  ``globus_sdk.exc`` is imported:

  - ``GlobusConnectionError``
  - ``GlobusConnectionTimeoutError``
  - ``GlobusTimeoutError``
  - ``NetworkError``
