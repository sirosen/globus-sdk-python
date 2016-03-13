from __future__ import print_function

from globus_sdk.base import BaseClient, merge_params
from globus_sdk import exc


def paginated_resource(page_size, default_limit, max_total_results):
    """
    A decorator that describes paginated Transfer API resources.
    This is not a top level helper func because it depends upon the pagination
    implementation of the Transfer API, which may not be the implementation
    chosen by other, future APIs.

    A more complex and generic version of this generalization, as a
    PaginatedResource class from which various API resources inherit is
    possible, but it requires that individually defined API resources
    "know" how to request the next page. We chose not to do this because of the
    complexity and limited need for it at present.

    When using this decorator, it is a good idea to name the arguments, even
    though they are positionals, for greater clarity inline.
    As in

    >>> @paginated_resource(page_size=25, default_limit=25,
    >>>                     max_total_results=250)
    >>> def call_that_supports_paging(...):
    >>>     ...

    Expectations about Paginated Transfer API Resources:
    - They support `limit` and `offset` query params, with `limit` being a
      count of elements to return, and offset being an offset into the result
      set (as opposed to a page number)
    - They return a JSON result with `has_next_page` as a boolean key,
      indicating whether or not there are more results available -- even if the
      hard limit for the API forbids requesting these results
    - Individual results are JSON objects inside of an array named `DATA` in
      the returned JSON document.
    """

    def wrapper(func):
        """
        Inner decorator returned by paginated_resource being called on its
        arguments.
        """

        def wrapped_func(*args, **kwargs):
            """
            Go a level deeper to produce a function which wraps the function
            that wrapper() is being applied to! This is obvious and intuitive!

            Explanation:
            paginated_resource is used as a decorator, but takes arguments, so
            it needs to be defined as a function on those arguments which
            returns a decorator.
            That decorator is wrapper().
            wrapper() is a decorator which takes a function, and returns a
            paginated version of that function. But wrapper(), being a
            decorator, is a transformation that runs at function definition
            time, so it in turn needs to create a closure over the paginated
            function that does what we want, and return that.
            That closure, created by the decorator wrapper(), is
            wrapped_func().
            Got it? Good.

            Furthermore, paginated resources have their paginated behavior IFF
            paginated=True is passed. Since that's an argument that callers of
            the resource, not the SDK writers, control, it goes deep in here,
            in the wrapped_func.

            Why does wrapped_func take "self" as its first argument? Well,
            because this is decorating the methods of TransferClient, after
            all! When decorating a method, the function returned by the
            decorator is a method as well, so it takes the implicit "self" arg
            as all methods do.
            """
            # pull desired values out of kwargs so that we don't disrupt the
            # flow of original positional arguments to the wrapped function,
            # `func`
            # this is messiness because a function definition can't read as
            # def f(*args, a=1, **kwargs): ...

            # pull out the paginate=True/False, but then delete it from kwargs
            # so that we don't pass it to the API as a query param
            paginated = kwargs.get('paginate', False)
            # use pop() over del to avoid a KeyError if absent
            kwargs.pop('paginate', None)

            limit = kwargs.get('limit', default_limit)
            # offset should rarely be set, but we need to handle the case in
            # which a caller wants to start their results at a given offset
            # manually
            offset = kwargs.get('offset', 0)

            # this is a bit of a naming issue -- the parameter we'll pass to
            # the API is named "limit", but we want to expose this to the
            # caller as a "limit" keyword arg
            # to resolve, just rename the "limit" we're given at the start of
            # the call to "given_limit"
            given_limit = limit
            # now, cap the limit per request to the page size
            limit = min(limit, page_size)

            has_next_page = True

            while has_next_page:
                # check the offset to see if it exceeds the maximum total
                # number of results allowed by the API
                if offset > max_total_results:
                    raise exc.PaginationOverrunError((
                        'Paginated call exceeded API limit. Try being more '
                        'restrictive with the results you request, or pass a '
                        'smaller limit to the paginated call you are making.'))

                # if we're about to request more results than the user asked
                # for, limit ourselves on the last paginated call to the API
                # TODO: is there a clearer way of expressing this arithmetic so
                # that it's more obviously correct?
                if offset + limit > given_limit:
                    limit = given_limit - offset

                kwargs['offset'] = offset
                kwargs['limit'] = limit

                res = func(*args, **kwargs).json_body

                # walk the results from the page we fetched, returning them as
                # the iterated elements
                for item in res['DATA']:
                    yield item

                # do we have another page of results to fetch?
                # always False if we're not paginated
                # also false if we've reached the given limit
                has_next_page = (res['has_next_page']
                                 and paginated
                                 and offset < given_limit)

                offset += limit

        return wrapped_func

    return wrapper


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

    @paginated_resource(page_size=100, default_limit=25, max_total_results=999)
    def endpoint_search(self, filter_fulltext, filter_scope=None, **params):
        """
        GET /endpoint_search?filter_fulltext=<filter_fulltext>
                            &filter_scope=<filter_scope>

        Additional params and valid filter_scopes are documented at
        https://docs.globus.org/api/transfer/endpoint_search


        # Examples
        Search for a given string as a fulltext search:
        >>> endpoint_search('String to search for!')

        Search for a given string, but only on endpoints that you own:
        >>> endpoint_search('foo', filter_scope='my-endpoints')
        """
        merge_params(params, filter_scope=filter_scope,
                     filter_fulltext=filter_fulltext)
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
