* New tools for working with optional and dependent scope strings (:pr:`553`)

  * A new class is provided for constructing optional and dependent scope
    strings, ``MutableScope``. Import as in
    ``from globus_sdk.scopes import MutableScope``

  * ``ScopeBuilder`` objects provide a method, ``make_mutable``, which converts
    from a scope name to a ``MutableScope`` object. See documentation on scopes
    for usage details
