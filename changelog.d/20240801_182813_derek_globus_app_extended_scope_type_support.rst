
Added
~~~~~

-   Added support for ``ScopeCollectionType`` to GlobusApp's ``__init__`` and
    ``add_scope_requirements`` methods. (:pr:`1020`)

Changed
~~~~~~~

-   Updated ``ScopeCollectionType`` to be defined recursively. (:pr:`1020`)


Development
~~~~~~~~~~~

-   Added a scope normalization function ``globus_sdk.scopes.scopes_to_scope_list`` to
    translate from ``ScopeCollectionType`` to a list of ``Scope`` objects.
    (:pr:`1020`)

