import inspect
import functools

from globus_sdk import exc
from globus_sdk.response import GlobusResponse


class PaginatedResource(object):
    """
    A decorator that describes paginated Transfer API resources.
    This is not a top level helper func because it depends upon the pagination
    implementation of the Transfer API, which may not be the implementation
    chosen by other, future APIs.

    Expectations about Paginated Transfer API Resources:
    - They support `limit` and `offset` query params, with `limit` being a
      count of elements to return, and offset being an offset into the result
      set (as opposed to a page number), 0-based
    - They return a JSON result with `has_next_page` as a boolean key,
      indicating whether or not there are more results available -- even if the
      hard limit for the API forbids requesting these results
    - Individual results are JSON objects inside of an array named `DATA` in
      the returned JSON document
    """
    # pages have 'has_next_page', 'offset', and 'limit'
    PAGING_STYLE_HAS_NEXT = 0
    # pages have 'offset', 'limit', and 'total'
    PAGING_STYLE_TOTAL = 1
    # pages have a 'has_next_page', but use 'last_key' rather than 'offset' +
    # 'limit'
    PAGING_STYLE_LAST_KEY = 2

    def __init__(self, max_results_per_call, max_total_results,
                 paging_style=PAGING_STYLE_HAS_NEXT):
        """
        PaginatedResource takes two arguments
        max_results_per_call is the max size of a page to fetch from the API.
        max_total_results is a pagination limit for total results to return
        from the API.

        When using this decorator, it is a good idea to name the arguments,
        even though they are positionals, for greater clarity inline, as in

        >>> @PaginatedResource(max_results_per_call=25, max_total_results=250)
        >>> def call_that_supports_paging(...):
        >>>     ...
        """
        self.max_results_per_call = max_results_per_call
        self.max_total_results = max_total_results
        self.paging_style = paging_style

    def _get_paging_kwargs(self, func, **kwargs):
        """
        Small helper for tidiness. Pulls some values out of kwargs, as
        desired.

        We need to pull desired values out of kwargs so that we don't
        disrupt the flow of original positional arguments to the wrapped
        function, `func`
        """
        # get the default values for keyword arguments to `func`
        argspec = inspect.getargspec(func)
        # getargspec has a kind of weird return value -- we need to manually
        # join together default kwarg names with their values
        defaults = dict(zip(argspec.args[-len(argspec.defaults):],
                            argspec.defaults))

        # get from kwargs, failover to wrapped functions kwarg defaults,
        # failover to None
        num_results = kwargs.get('num_results',
                                 defaults.get('num_results',
                                              None)
                                 )

        # paginated calls must always define a `num_results` kwarg, and this
        # would indicate that it wasn't passed and is missing from default
        # kwargs on the decorated function, or was passed as None explicitly
        if num_results is None:
            raise ValueError('Paginated Calls Must Supply `num_results`')

        # offset should rarely be set, but we need to handle the case in
        # which a caller wants to start their results at a given offset
        # manually
        offset = kwargs.get('offset', 0)

        return num_results, offset

    def __call__(self, func):
        """
        The "real" function decorator.

        i.e. it's the result of creating a PaginatedResource(...), and applying
        it to a function with the @<decorator> syntax.
        """

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            """
            This is a closure over the wrapped function -- a paginated version
            of that function. Lets us write paginated calls as though they were
            single API calls, and get paginated results via an iterator
            interface.
            """
            # keyword args used by the paging itself
            num_results, offset = self._get_paging_kwargs(func, **kwargs)

            # now, cap the limit per request to the max per request size
            limit = min(num_results, self.max_results_per_call)

            # check the requested num results to see if it exceeds the maximum
            # total number of results allowed by the API
            # only check if there is a max_total_results though
            if (self.max_total_results is not None and
                    num_results > self.max_total_results):
                raise exc.PaginationOverrunError((
                    'Paginated call would exceed API limit. Pass a smaller '
                    'num_results parameter -- the maximum for this call is {}')
                    .format(self.max_total_results))

            has_next_page = True
            while has_next_page:
                # if we're about to request more results than the user asked
                # for, limit ourselves on the last paginated call to the API
                if offset + limit > num_results:
                    limit = num_results - offset

                kwargs['offset'] = offset
                kwargs['limit'] = limit

                res = func(*args, **kwargs).json_body

                # walk the results from the page we fetched, returning them as
                # the iterated elements
                for item in res['DATA']:
                    yield GlobusResponse(item)

                offset += self.max_results_per_call

                # do we have another page of results to fetch?
                if self.paging_style == self.PAGING_STYLE_HAS_NEXT:
                    # set to False if we've reached the given limit
                    has_next_page = res['has_next_page']
                elif self.paging_style == self.PAGING_STYLE_TOTAL:
                    has_next_page = offset < res['total']
                else:
                    raise ValueError(
                        'Invalid Paging Style Given to PaginatedResource')

                has_next_page = has_next_page and offset < num_results

        # we're still in __call__ here -- return the closure we just defined
        return wrapped_func
