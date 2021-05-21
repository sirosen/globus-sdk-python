from .base import Paginator


class LastKeyPaginator(Paginator):
    def __init__(self, method, client_args, client_kwargs):
        self.method = method
        self.last_key = None
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self):
        has_next_page = True
        while has_next_page:
            if self.last_key:
                self.client_kwargs["last_key"] = self.last_key
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            self.last_key = current_page.get("last_key")
            has_next_page = current_page["has_next_page"]
