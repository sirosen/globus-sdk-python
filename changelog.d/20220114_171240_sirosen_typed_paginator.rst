* Add ``Paginator.wrap`` as a method for getting a paginated methods. This interface is more
  verbose than the existing ``paginated`` methods, but correctly preserves type
  annotations. It is therefore preferable for users who are using ``mypy`` to do
  type checking. (:pr:`494`)
