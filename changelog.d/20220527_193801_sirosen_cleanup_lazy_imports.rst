* Imports from ``globus_sdk`` are now evaluated lazily via module-level
  ``__getattr__`` on python 3.7+ (:pr:`NUMBER`)

  * This improves the performance of imports for almost all use-cases, in some
    cases by over 80%

  * The method ``globus_sdk._force_eager_imports()`` can be used to force
    non-lazy imports, for latency sensitive applications which wish to control
    when the time cost of import evaluation is paid. This method is private and is
    therefore is not covered under the ``globus-sdk``'s SemVer guarantees, but it is
    expected to remain stable for the foreseeable future.
