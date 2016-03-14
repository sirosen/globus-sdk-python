from __future__ import print_function

import functools

from globus_sdk.base import BaseClient, merge_params
from globus_sdk import exc


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

    def __init__(self, max_results_per_call, max_total_results):
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

    def _get_paging_kwargs(self, **kwargs):
        """
        Small helper for tidiness. Pulls some values out of kwargs, as
        desired.

        We need to pull desired values out of kwargs so that we don't
        disrupt the flow of original positional arguments to the wrapped
        function, `func`
        """
        # paginated calls should always define a `num_results` kwarg, but just
        # in case someone forgets to do so, we can fall back on the max allowed
        num_results = kwargs.get('num_results', self.max_results_per_call)

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
            num_results, offset = self._get_paging_kwargs(**kwargs)

            # now, cap the limit per request to the max per request size
            limit = min(num_results, self.max_results_per_call)

            # check the requested num results to see if it exceeds the maximum
            # total number of results allowed by the API
            if num_results > self.max_total_results:
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
                    yield item

                offset += self.max_results_per_call

                # do we have another page of results to fetch?
                # set to False if we've reached the given limit
                has_next_page = res['has_next_page'] and offset < num_results

        # we're still in __call__ here -- return the closure we just defined
        return wrapped_func


class TransferClient(BaseClient):
    error_class = exc.TransferAPIError

    def __init__(self, environment="default"):
        BaseClient.__init__(self, "transfer", environment, "/v0.10/")

    # Convenience methods, providing more pythonic access to common REST
    # resources
    # TODO: Is there consensus that we want to maintain these? I feel
    # strongly that we shouldn't provide anything more complex, e.g.
    # hard coding param names and document types, but wouldn't be too
    # bad to maintain these.
    def get_endpoint(self, endpoint_id, **kw):
        """GET /endpoint/<endpoint_id>"""
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.get(path, params=kw)

    def update_endpoint(self, endpoint_id, data, **kw):
        """PUT /endpoint/<endpoint_id>"""
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.put(path, data, params=kw)

    def create_endpoint(self, data):
        """POST /endpoint/<endpoint_id>"""
        return self.post("endpoint", data)

    @PaginatedResource(max_results_per_call=100, max_total_results=1000)
    def endpoint_search(self, filter_fulltext, filter_scope=None,
                        num_results=25, **params):
        """
        GET /endpoint_search?filter_fulltext=<filter_fulltext>
                            &filter_scope=<filter_scope>

        Additional params and valid filter_scopes are documented at
        https://docs.globus.org/api/transfer/endpoint_search

        This method acts as an iterator, returning results from the API as
        python dictionaries built from JSON documents.

        # Simple Examples
        Search for a given string as a fulltext search:
        >>> for ep in endpoint_search('String to search for!'):
        >>>     print(ep['display_name'])

        Search for a given string, but only on endpoints that you own:
        >>> for ep in endpoint_search('foo', filter_scope='my-endpoints'):
        >>>     print('{} has ID {}'.format(ep['display_name'], ep['id']))

        Search results are capped at a number of elements equal to the
        `num_results` parameter.
        If you want more than the default, 25, elements, do like so:

        >>> for ep in endpoint_search('String to search for!',
        >>>                           num_results=120):
        >>>     print(ep['display_name'])

        It is very important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query. If you attempt to exceed this
        limit, you will trigger a PaginationOverrunError.

        >>> for ep in endpoint_search('globus', # a very common string
        >>>                           num_results=1200):
        >>>     print(ep['display_name'])

        will trigger this error.
        """
        merge_params(params, filter_scope=filter_scope,
                     filter_fulltext=filter_fulltext, num_results=num_results)
        return self.get("endpoint_search", params=params)

    def endpoint_autoactivate(self, endpoint_id, **params):
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def operation_ls(self, endpoint_id, **params):
        path = self.qjoin_path("endpoint", endpoint_id, "ls")
        return self.get(path, params=params)


def _get_client_from_args():
    import sys

    if len(sys.argv) < 2:
        print("Usage: %s token_file [environment]" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as f:
        token = f.read().strip()

    if len(sys.argv) > 2:
        environment = sys.argv[2]
    else:
        environment = "default"

    api = TransferClient(environment)
    api.set_auth_token(token)
    return api


if __name__ == '__main__':
    api = _get_client_from_args()
