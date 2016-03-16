from __future__ import print_function

from globus_sdk import exc
from globus_sdk.base import BaseClient, merge_params
from globus_sdk.transfer.paging import PaginatedResource


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
    def endpoint_search(self, filter_fulltext=None, filter_scope=None,
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
                     filter_fulltext=filter_fulltext)
        return self.get("endpoint_search", params=params)

    def endpoint_autoactivate(self, endpoint_id, **params):
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def endpoint_server_list(self, endpoint_id, **params):
        path = self.qjoin_path('endpoint', endpoint_id, 'server_list')
        for server in self.get(path, params=params).json_body['DATA']:
            yield server

    def my_shared_endpoint_list(self, endpoint_id, **params):
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_shared_endpoint_list')
        for ep in self.get(path, params=params).json_body['DATA']:
            yield ep

    def endpoint_role_list(self, endpoint_id, **params):
        path = self.qjoin_path('endpoint', endpoint_id, 'role_list')
        for role in self.get(path, params=params).json_body['DATA']:
            yield role

    def endpoint_acl_list(self, endpoint_id, **params):
        path = self.qjoin_path('endpoint', endpoint_id, 'access_list')
        for rule in self.get(path, params=params).json_body['DATA']:
            yield rule

    def bookmark_list(self, **params):
        for bookmark in self.get('bookmark_list',
                                 params=params).json_body['DATA']:
            yield bookmark

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_list(self, num_results=10, **params):
        return self.get('task_list', params=params)

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_event_list(self, task_id, num_results=10, **params):
        path = self.qjoin_path('task', task_id, 'event_list')
        return self.get(path, params=params)

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
