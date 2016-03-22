from __future__ import print_function

import json

from globus_sdk import exc, config
from globus_sdk.response import GlobusResponse, GlobusHTTPResponse
from globus_sdk.base import BaseClient, merge_params
from globus_sdk.transfer.paging import PaginatedResource


class TransferResponse(GlobusHTTPResponse):
    def __str__(self):
        return json.dumps(self.json_body, indent=2)


class TransferClient(BaseClient):
    error_class = exc.TransferAPIError
    response_class = TransferResponse

    def __init__(self, environment=config.get_default_environ(),
                 auth_token=None):
        BaseClient.__init__(self, "transfer", environment, "/v0.10/",
                            auth_token=auth_token)

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

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

    def delete_endpoint(self, endpoint_id):
        """
        DELETE /endpoint/<endpoint_id>
        """
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.delete(path)

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
        """
        POST /endpoint/<endpoint_id>/autoactivate
        """
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def my_shared_endpoint_list(self, endpoint_id, **params):
        """
        GET /endpoint/<endpoint_id>/my_shared_endpoint_list
        """
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_shared_endpoint_list')
        for ep in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(ep)

    def my_effective_pause_rule_list(self, endpoint_id, **params):
        """
        GET /endpoint/<endpoint_id>/my_effective_pause_rule_list
        """
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_effective_pause_rule_list')
        for rule in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(rule)

    # Endpoint servers

    def endpoint_server_list(self, endpoint_id, **params):
        """
        GET /endpoint/<endpoint_id>/server_list
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server_list')
        for server in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(server)

    def get_endpoint_server(self, endpoint_id, server_id):
        """
        GET /endpoint/<endpoint_id>/server/<server_id>
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.get(path)

    def add_endpoint_server(self, endpoint_id, server_data):
        """
        POST /endpoint/<endpoint_id>/server
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server')
        return self.post(path, server_data)

    def update_endpoint_server(self, endpoint_id, server_id, server_data):
        """
        POST /endpoint/<endpoint_id>/server/<server_id>
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.post(path, server_data)

    def delete_endpoint_server(self, endpoint_id, server_id):
        """
        DELETE /endpoint/<endpoint_id>/server/<server_id>
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.delete(path)

    #
    # Access Management
    #

    def endpoint_role_list(self, endpoint_id, **params):
        """
        GET /endpoint/<endpoint_id>/role_list
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'role_list')
        for role in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(role)

    def endpoint_acl_list(self, endpoint_id, **params):
        """
        GET /endpoint/<endpoint_id>/access_list
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access_list')
        for rule in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(rule)

    def bookmark_list(self, **params):
        """
        GET /bookmark_list
        """
        for bookmark in self.get('bookmark_list',
                                 params=params).json_body['DATA']:
            yield GlobusResponse(bookmark)

    # Synchronous Filesys Operations

    def operation_ls(self, endpoint_id, **params):
        """
        GET /operation/endpoint/<endpoint_id>/ls
        """
        path = self.qjoin_path("operation/endpoint", endpoint_id, "ls")
        return self.get(path, params=params)

    def operation_mkdir(self, endpoint_id, path, **params):
        """
        POST /operation/endpoint/<endpoint_id>/mkdir
        """
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id,
                                        "mkdir")
        json_body = {
            'DATA_TYPE': 'mkdir',
            'path': path
        }
        return self.post(resource_path, json_body=json_body, params=params)

    def operation_rename(self, endpoint_id, oldpath, newpath, **params):
        """
        POST /operation/endpoint/<endpoint_id>/rename
        """
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id,
                                        "rename")
        json_body = {
            'DATA_TYPE': 'mkdir',
            'old_path': oldpath,
            'new_path': newpath
        }
        return self.post(resource_path, json_body=json_body, params=params)

    # Task Submission

    def get_submission_id(self, **params):
        """
        GET /submission_id
        """
        return self.get("submission_id", params=params)

    def submit_transfer(self, data):
        """
        POST /transfer
        """
        return self.post('/transfer', data)

    def submit_delete(self, data):
        """
        POST /delete
        """
        return self.post('/delete', data)

    # Task inspection and management

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_list(self, num_results=10, **params):
        """
        GET /task_list
        """
        return self.get('task_list', params=params)

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_event_list(self, task_id, num_results=10, **params):
        """
        GET /task/<task_id>/event_list
        """
        path = self.qjoin_path('task', task_id, 'event_list')
        return self.get(path, params=params)

    def get_task(self, task_id, **params):
        """
        GET /task/<task_id>
        """
        resource_path = self.qjoin_path("task", task_id)
        return self.get(resource_path, params=params)

    def update_task(self, task_id, data, **params):
        """
        PUT /task/<task_id>
        """
        resource_path = self.qjoin_path("task", task_id)
        return self.put(resource_path, data, params=params)

    def cancel_task(self, task_id):
        """
        POST /task/<task_id>/cancel
        """
        resource_path = self.qjoin_path("task", task_id, "cancel")
        return self.post(resource_path)

    def task_pause_info(self, task_id):
        """
        POST /task/<task_id>/pause_info
        """
        resource_path = self.qjoin_path("task", task_id, "pause_info")
        return self.get(resource_path)
