from .base import Paginator


class MarkerPaginator(Paginator):
    """
    A paginator which uses `has_next_page` and `marker` from payloads, sets the `marker`
    query param to page.

    This is the default method for GCS pagination, so it's very simple.
    """

    def __init__(self, method, client_args, client_kwargs):
        """
        **Parameters**

        ``method``
          A bound method of an SDK client, used to generate a paginated variant

        ``client_args``
          Arguments to the underlying method which are passed when the paginator is
          instantiated. i.e. given ``client.paginated.foo(a, b, c=1)``, this will be
          ``[a, b]``. The paginator will pass these arguments to *each* call of the
          bound method as it pages.

        ``client_kwargs``
          Keyword arguments to the underlying method, like ``client_args`` above.
          ``client.paginated.foo(a, b, c=1)`` will pass this as ``{"c": 1}``. As with
          ``client_args``, it's passed to each paginated call.
        """
        self.method = method
        self.marker = None
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self):
        has_next_page = True
        while has_next_page:
            if self.marker:
                self.client_kwargs["marker"] = self.marker
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.marker = current_page.get("marker")
            has_next_page = current_page.get("has_next_page", False)
