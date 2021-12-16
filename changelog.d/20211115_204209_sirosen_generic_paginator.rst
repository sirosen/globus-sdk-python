* `Paginator` objects are now generics over a type var for their page type. The
  page type is bounded by `GlobusHTTPResponse`, and most type-checker behaviors
  will remain unchanged (:pr:`495`)
