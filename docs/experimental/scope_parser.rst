.. _experimental_scope_parser:

Scope Parser
============

.. currentmodule:: globus_sdk.experimental.scope_parser

This component defines a Scope object and exposes use of a parser which can
parse scope strings into trees of Scope objects.
It should be regarded as very similar to the existing ``MutableScope`` object in
``globus_sdk.scopes``. Key differences from ``MutableScope``:

- ``Scope.parse`` is available, for parsing scopes from strings
- The Globus SDK does not support using ``Scope`` in all of the locations where
  ``MutableScope`` is supported -- Scope objects must be stringified for use
- ``Scope`` objects define a ``_contains__`` method, allowing one to check if one scope
  properly contains another

.. warning::

    This module is experimental due to the limitations of scope strings as a
    representation of consent trees. The scope trees produced by parsing do
    not necessarily describe real consent structures in Globus Auth.

Reference
---------

.. autoclass:: Scope
   :members:
   :member-order: bysource
   :special-members:

.. autoclass:: ScopeParseError

.. autoclass:: ScopeCycleError
