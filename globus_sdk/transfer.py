from __future__ import print_function

from globus_sdk.base import BaseClient, merge_params
from globus_sdk import exc


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

    def endpoint_search_iterator(self, *args, **kwargs):
        """
        Wrap endpoint_search calls in an iterator that walks over the paginated
        results, returning the search result objects themselves (rather than
        the wrapping JSON object, which isn't relevant in this context).
        """
        has_next_page = True
        offset = 0
        limit = 100
        while has_next_page:
            kwargs['offset'] = offset
            kwargs['limit'] = limit
            res = self.endpoint_search(*args, **kwargs).json_body
            for item in res['DATA']:
                yield item

            has_next_page = res['has_next_page']
            offset += limit
            # transfer caps at offset=999, so harshly end the search here if
            # that's what we were given
            if offset > 999:
                has_next_page = False


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
