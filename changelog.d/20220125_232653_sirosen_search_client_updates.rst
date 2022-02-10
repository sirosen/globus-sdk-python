* Add support for scroll queries to ``SearchClient``. ``SearchClient.scroll``
  and ``SearchClient.paginated.scroll`` are now available as methods, and a new
  helper class, ``SearchScrollQuery``, can be used to easily construct
  scrolling queries. (:pr:`507`)
