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


MissingType and MISSING
-----------------------

The ``MISSING`` sentinel value is used as an alternative to ``None`` in APIs
which accept ``null`` as a valid value. Whenever ``MISSING`` is included in a
request, it will be removed before the request is sent to the service.

As a result, where ``MISSING`` is used as the default for a value, ``None`` can
be used to explicitly pass the value ``null``.

.. py:class:: globus_sdk.MissingType

    This is the type of ``MISSING``.

.. py:data:: globus_sdk.MISSING

    The ``MISSING`` sentinel value. It is a singleton.
