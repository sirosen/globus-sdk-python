from .base import Paginator


class _LimitOffsetBasedPaginator(Paginator):
    def __init__(
        self,
        method,
        get_page_size,
        max_total_results,
        page_size,
        client_args,
        client_kwargs,
    ):
        self.method = method
        self.get_page_size = get_page_size
        self.client_args = client_args
        self.client_kwargs = client_kwargs

        self.max_total_results = max_total_results
        self.limit = page_size
        self.offset = 0

    def _update_limit(self):
        if (
            self.max_total_results is not None
            and self.offset + self.limit > self.max_total_results
        ):
            self.limit = self.max_total_results - self.offset
        self.client_kwargs["limit"] = self.limit

    def _update_and_check_offset(self, current_page):
        self.offset += self.get_page_size(current_page)
        self.client_kwargs["offset"] = self.offset
        return (
            self.max_total_results is not None and self.offset >= self.max_total_results
        )


class HasNextPaginator(_LimitOffsetBasedPaginator):
    def __iter__(self):
        has_next_page = True
        while has_next_page:
            self._update_limit()
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            if self._update_and_check_offset(current_page):
                return
            has_next_page = current_page["has_next_page"]


class LimitOffsetTotalPaginator(_LimitOffsetBasedPaginator):
    def __iter__(self):
        has_next_page = True
        while has_next_page:
            self._update_limit()
            current_page = self.method(*self.client_args, **self.client_kwargs)
            yield current_page
            if self._update_and_check_offset(current_page):
                return
            has_next_page = self.offset < current_page["total"]
