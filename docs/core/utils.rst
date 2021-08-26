Utilities
=========

.. warning::

    The components in this module are *not* intended for outside use, but are
    internal to the Globus SDK.

    They may change in backwards-incompatible ways in minor or patch releases
    of the SDK.

    This documentation is included here for completeness.

PayloadWrapper
--------------

The ``PayloadWrapper`` class is used as a base class for all Globus SDK
payload datatypes to provide nicer interfaces for payload construction.

The objects are a type of ``UserDict`` with no special methods.

.. autoclass:: globus_sdk.utils.PayloadWrapper
