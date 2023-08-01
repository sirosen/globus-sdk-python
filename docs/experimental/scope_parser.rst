.. _experimental_scope_parser:

Scope Parser
============

.. currentmodule:: globus_sdk.experimental.scope_parser

This component defines a ``Scope`` object and exposes use of a parser which can
parse scope strings into trees of ``Scope`` objects.
It should be regarded as very similar to the existing ``MutableScope`` object in
``globus_sdk.scopes``. Key differences from ``MutableScope``:

- ``Scope.parse`` is available, for parsing scopes from strings
- The Globus SDK does not support using ``Scope`` in all of the locations where
  ``MutableScope`` is supported -- Scope objects must be stringified for use
- ``Scope`` objects define a ``__contains__`` method, allowing one to check if one scope
  properly contains another

.. note::

    The scope trees produced by parsing represent prospective consent structures as
    would be produced by a single authentication flow in Auth. No external APIs (e.g.,
    the Get Consents API) are used to validate or mutate the data.

Reference
---------

.. autoclass:: Scope
   :members:
   :member-order: bysource
   :special-members:

.. autoclass:: ScopeParseError

.. autoclass:: ScopeCycleError
