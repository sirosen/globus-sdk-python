from .base import Paginator


class NextTokenPaginator(Paginator):
    """
    A paginator which uses `next_token` from payloads to set the `next_token`
    query param to page.

    Very similar to GCS's marker paginator, but only used for Transfer's
    get_shared_endpoint_list
    """

    def __init__(self, method, *, items_key=None, client_args, client_kwargs):
        super().__init__(
            method,
            items_key=items_key,
            client_args=client_args,
            client_kwargs=client_kwargs,
        )
        self.next_token = None

    def pages(self):
        has_next_page = True
        while has_next_page:
            if self.next_token:
                self.client_kwargs["next_token"] = self.next_token
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.next_token = current_page.get("next_token")
            has_next_page = current_page.get("next_token") is not None
