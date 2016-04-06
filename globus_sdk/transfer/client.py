from __future__ import print_function

import json

from globus_sdk import exc, config
from globus_sdk.response import GlobusResponse, GlobusHTTPResponse
from globus_sdk.base import BaseClient, merge_params
from globus_sdk.transfer.paging import PaginatedResource


class TransferResponse(GlobusHTTPResponse):
    """
    Custom response for TransferClient, which relies on the fact that the
    body is always json to make printing the response more friendly.
    """
    def __str__(self):
        return json.dumps(self.json_body, indent=2)


class TransferClient(BaseClient):
    """
    Client for the
    `Globus Transfer API <https://docs.globus.org/api/transfer/>`_.

    This class provides helper methods for most common resources in the
    REST API, and basic ``get``, ``put``, ``post``, and ``delete`` methods
    from the base rest client that can be used to access any REST resource.

    There are two types of helper methods: list methods which return an
    iterator of :class:`GlobusResponse <globus_sdk.response.GlobusResponse>`
    objects, and simple methods that return a single
    :class:`GlobusHTTPResponse <globus_sdk.response.GlobusHTTPResponse>`
    object. Detailed documentation is available in the official REST API
    documentation, which is linked to from the method documentation. Methods
    that allow arbitrary keyword arguments will pass the extra arguments as
    query parameters.
    """

    error_class = exc.TransferAPIError
    response_class = TransferResponse

    def __init__(self, environment=config.get_default_environ(),
                 token=None):
        BaseClient.__init__(self, "transfer", environment, "/v0.10/",
                            token=token)

    def config_load_token(self):
        return config.get_transfer_token(self.environment)

    # Convenience methods, providing more pythonic access to common REST
    # resources

    #
    # Endpoint Management
    #

    def get_endpoint(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>``

        See
        `Get Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.get(path, params=params)

    def update_endpoint(self, endpoint_id, data, **params):
        """
        ``PUT /endpoint/<endpoint_id>``

        See
        `Update Endpoint by ID \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.put(path, data, params=params)

    def create_endpoint(self, data):
        """
        ``POST /endpoint/<endpoint_id>``

        See
        `Create endpoint \
        <https://docs.globus.org/api/transfer/endpoint/#create_endpoint>`_
        in the REST documentation for details.
        """
        return self.post("endpoint", data)

    def delete_endpoint(self, endpoint_id):
        """
        ``DELETE /endpoint/<endpoint_id>``

        See
        `Delete endpoint by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.delete(path)

    @PaginatedResource(max_results_per_call=100, max_total_results=1000)
    def endpoint_search(self, filter_fulltext=None, filter_scope=None,
                        num_results=25, **params):
        r"""
        .. parsed-literal::

            GET /endpoint_search\
            ?filter_fulltext=<filter_fulltext>&filter_scope=<filter_scope>

        Additional params and valid filter_scopes are documented at
        https://docs.globus.org/api/transfer/endpoint_search

        This method acts as an iterator, returning results from the API as
        :class:`GlobusResponse <globus_sdk.response.GlobusResponse>`
        objects wrapping python dictionaries built from JSON documents.

        Search for a given string as a fulltext search:

        >>> for r in endpoint_search('String to search for!'):
        >>>     print(r.data['display_name'])

        Search for a given string, but only on endpoints that you own:

        >>> for r in endpoint_search('foo', filter_scope='my-endpoints'):
        >>>     print('{} has ID {}'.format(r.data['display_name'], ep['id']))

        Search results are capped at a number of elements equal to the
        ``num_results`` parameter.
        If you want more than the default, 25, elements, do like so:

        >>> for r in endpoint_search('String to search for!',
        >>>                          num_results=120):
        >>>     print(r.data['display_name'])

        It is very important to be aware that the Endpoint Search API limits
        you to 1000 results for any search query. If you attempt to exceed this
        limit, you will trigger a PaginationOverrunError.

        >>> for r in endpoint_search('globus', # a very common string
        >>>                          num_results=1200):
        >>>     print(r.data['display_name'])

        will trigger this error.
        """
        merge_params(params, filter_scope=filter_scope,
                     filter_fulltext=filter_fulltext)
        return self.get("endpoint_search", params=params)

    def endpoint_autoactivate(self, endpoint_id, **params):
        """
        ``POST /endpoint/<endpoint_id>/autoactivate``

        See
        `Autoactivate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#autoactivate_endpoint>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def endpoint_deactivate(self, endpoint_id, **params):
        """
        ``POST /endpoint/<endpoint_id>/deactivate``

        See
        `Deactive endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#deactivate_endpoint>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id, "deactivate")
        return self.post(path, params=params)

    def endpoint_activate(self, endpoint_id, data, **params):
        """
        ``POST /endpoint/<endpoint_id>/activate``

        See
        `Activate endpoint \
        <https://docs.globus.org/api/transfer/endpoint_activation/#autoactivate_endpoint>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def endpoint_get_activation_requirements(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/activation_requirements``

        See
        `Get activation requirements \
        <https://docs.globus.org/api/transfer/endpoint_activation/#get_activation_requirements>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path("endpoint", endpoint_id, "autoactivate")
        return self.post(path, params=params)

    def my_shared_endpoint_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/my_shared_endpoint_list``

        See
        `Get shared endpoint list \
        <https://docs.globus.org/api/transfer/endpoint/#get_shared_endpoint_list>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_shared_endpoint_list')
        for ep in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(ep)

    def my_effective_pause_rule_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/my_effective_pause_rule_list``

        See
        `Get my effective endpoint pause rules \
        <https://docs.globus.org/api/transfer/endpoint/#get_my_effective_endpoint_pause_rules>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id,
                               'my_effective_pause_rule_list')
        for rule in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(rule)

    # Endpoint servers

    def endpoint_server_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/server_list``

        See
        `Get endpoint server list \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_list>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server_list')
        for server in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(server)

    def get_endpoint_server(self, endpoint_id, server_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/server/<server_id>``

        See
        `Get endpoint server list \
        <https://docs.globus.org/api/transfer/endpoint/#get_endpoint_server_list>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.get(path, params=params)

    def add_endpoint_server(self, endpoint_id, server_data):
        """
        ``POST /endpoint/<endpoint_id>/server``

        See
        `Add endpoint server \
        <https://docs.globus.org/api/transfer/endpoint/#add_endpoint_server>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server')
        return self.post(path, server_data)

    def update_endpoint_server(self, endpoint_id, server_id, server_data):
        """
        ``POST /endpoint/<endpoint_id>/server/<server_id>``

        See
        `Update endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#update_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.post(path, server_data)

    def delete_endpoint_server(self, endpoint_id, server_id):
        """
        ``DELETE /endpoint/<endpoint_id>/server/<server_id>``

        See
        `Delete endpoint server by id \
        <https://docs.globus.org/api/transfer/endpoint/#delete_endpoint_server_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'server', server_id)
        return self.delete(path)

    #
    # Roles
    #

    def endpoint_role_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/role_list``

        See
        `Get list of endpoint roles \
        <https://docs.globus.org/api/transfer/endpoint_roles/#get_list_of_endpoint_roles>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'role_list')
        for role in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(role)

    def add_endpoint_role(self, endpoint_id, role_data):
        """
        ``POST /endpoint/<endpoint_id>/role``

        See
        `Create endpoint role \
        <https://docs.globus.org/api/transfer/endpoint_roles/#create_endpoint_role>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'role')
        return self.post(path, role_data)

    def get_endpoint_role(self, endpoint_id, role_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/role/<role_id>``

        See
        `Get endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#get_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'role', role_id)
        return self.get(path, params=params)

    def delete_endpoint_role(self, endpoint_id, role_id):
        """
        ``DELETE /endpoint/<endpoint_id>/role/<role_id>``

        See
        `Delete endpoint role by id \
        <https://docs.globus.org/api/transfer/endpoint_roles/#delete_endpoint_role_by_id>`_
        in the REST documentation for details.
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'role', role_id)
        return self.delete(path)

    #
    # ACLs
    #

    def endpoint_acl_list(self, endpoint_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/access_list``
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access_list')
        for rule in self.get(path, params=params).json_body['DATA']:
            yield GlobusResponse(rule)

    def get_endpoint_acl_rule(self, endpoint_id, rule_id, **params):
        """
        ``GET /endpoint/<endpoint_id>/access/<rule_id>``
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.get(path, params=params)

    def add_endpoint_acl_rule(self, endpoint_id, rule_data):
        """
        ``POST /endpoint/<endpoint_id>/access``
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access')
        return self.post(path, rule_data)

    def update_endpoint_acl_rule(self, endpoint_id, rule_id, rule_data):
        """
        ``PUT /endpoint/<endpoint_id>/access/<rule_id>``
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.put(path, rule_data)

    def delete_endpoint_acl_rule(self, endpoint_id, rule_id):
        """
        ``DELETE /endpoint/<endpoint_id>/access/<rule_id>``
        """
        path = self.qjoin_path('endpoint', endpoint_id, 'access', rule_id)
        return self.delete(path)

    #
    # Bookmarks
    #

    def bookmark_list(self, **params):
        """
        ``GET /bookmark_list``
        """
        for bookmark in self.get('bookmark_list',
                                 params=params).json_body['DATA']:
            yield GlobusResponse(bookmark)

    def create_bookmark(self, bookmark_data):
        """
        ``POST /bookmark``
        """
        return self.post('bookmark', bookmark_data)

    def get_bookmark(self, bookmark_id, **params):
        """
        ``GET /bookmark/<bookmark_id>``
        """
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.get(path, params=params)

    def update_bookmark(self, bookmark_id, bookmark_data):
        """
        ``PUT /bookmark/<bookmark_id>``
        """
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.put(path, bookmark_data)

    def delete_bookmark(self, bookmark_id):
        """
        ``DELETE /bookmark/<bookmark_id>``
        """
        path = self.qjoin_path('bookmark', bookmark_id)
        return self.delete(path)

    #
    # Synchronous Filesys Operations
    #

    def operation_ls(self, endpoint_id, **params):
        """
        ``GET /operation/endpoint/<endpoint_id>/ls``
        """
        path = self.qjoin_path("operation/endpoint", endpoint_id, "ls")
        return self.get(path, params=params)

    def operation_mkdir(self, endpoint_id, path, **params):
        """
        ``POST /operation/endpoint/<endpoint_id>/mkdir``
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
        ``POST /operation/endpoint/<endpoint_id>/rename``
        """
        resource_path = self.qjoin_path("operation/endpoint", endpoint_id,
                                        "rename")
        json_body = {
            'DATA_TYPE': 'mkdir',
            'old_path': oldpath,
            'new_path': newpath
        }
        return self.post(resource_path, json_body=json_body, params=params)

    #
    # Task Submission
    #

    def get_submission_id(self, **params):
        """
        ``GET /submission_id``
        """
        return self.get("submission_id", params=params)

    def submit_transfer(self, data):
        """
        ``POST /transfer``
        """
        return self.post('/transfer', data)

    def submit_delete(self, data):
        """
        ``POST /delete``
        """
        return self.post('/delete', data)

    def make_submit_transfer_data(self, source_endpoint, dest_endpoint,
                                  transfer_items, label=None, sync_level=None,
                                  **kwargs):
        """
        Build a full document for submitting a Transfer.
        Takes an array of transfer items, a mandatory label for the Transfer,
        and an optional sync_level.
        For compatibility with older code and those knowledgeable about the API
        sync_level can be 1, 2, or 3, but it can also be
        "exists", "mtime", or "checksum" if you want greater clarity in
        client code.

        Includes fetching the submission ID as part of document generation. The
        submission ID can be pulled out of here to inspect, but the document
        can be used as-is multiple times over to retry a potential submission
        failure (so there shouldn't be any need to inspect it).
        """
        datadoc = {
            'DATA_TYPE': 'transfer',
            'submission_id': self.get_submission_id().data['value'],
            'source_endpoint': source_endpoint,
            'destination_endpoint': dest_endpoint,
            'DATA': transfer_items
        }

        # map the sync_level (if it's a nice string) to one of the known int
        # values
        # you can get away with specifying an invalid sync level -- the API
        # will just reject you with an error. This is kind of important: if
        # more levels are added in the future this method doesn't become
        # garbage overnight
        if sync_level is not None:
            sync_dict = {"exists": 1, "mtime": 2, "checksum": 3}
            sync_level = sync_dict.get(sync_level, sync_level)
            datadoc['sync_level'] = sync_level

        if label is not None:
            datadoc['label'] = label

        # any remaining arguments are global options for the Transfer document
        # pass them through verbatim
        for optional_arg in kwargs:
            datadoc[optional_arg] = kwargs[optional_arg]

        return datadoc

    def make_submit_transfer_item(self, source, dest, recursive=False):
        """
        Helper to build a single transfer item document (as a dict)
        Takes a source path, dest path, and recursivity, plugs them in and
        spits out the dict. In general, clients of the SDK should be using this
        to feed into make_transfer_data, but not inspecting the contents.
        """
        datadoc = {
            'DATA_TYPE': 'transfer_item',
            'source_path': source,
            'destination_path': dest
        }
        if recursive:
            datadoc['recursive'] = True

        return datadoc

    #
    # Task inspection and management
    #

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_list(self, num_results=10, **params):
        """
        ``GET /task_list``
        """
        return self.get('task_list', params=params)

    @PaginatedResource(max_results_per_call=1000, max_total_results=None,
                       paging_style=PaginatedResource.PAGING_STYLE_TOTAL)
    def task_event_list(self, task_id, num_results=10, **params):
        """
        ``GET /task/<task_id>/event_list``
        """
        path = self.qjoin_path('task', task_id, 'event_list')
        return self.get(path, params=params)

    def get_task(self, task_id, **params):
        """
        ``GET /task/<task_id>``
        """
        resource_path = self.qjoin_path("task", task_id)
        return self.get(resource_path, params=params)

    def update_task(self, task_id, data, **params):
        """
        ``PUT /task/<task_id>``
        """
        resource_path = self.qjoin_path("task", task_id)
        return self.put(resource_path, data, params=params)

    def cancel_task(self, task_id):
        """
        ``POST /task/<task_id>/cancel``
        """
        resource_path = self.qjoin_path("task", task_id, "cancel")
        return self.post(resource_path)

    def task_pause_info(self, task_id, **params):
        """
        ``POST /task/<task_id>/pause_info``
        """
        resource_path = self.qjoin_path("task", task_id, "pause_info")
        return self.get(resource_path, params=params)
