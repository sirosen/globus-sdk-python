from random import getrandbits
import globus_sdk
from tests.framework import (CapturedIOTestCase, get_client_data,
                             GO_EP1_ID, GO_EP2_ID,
                             GO_USER_ID, SDK_USER_ID,
                             SDKTESTER1A_NATIVE1_RT)
from globus_sdk.exc import TransferAPIError
from globus_sdk.transfer.paging import PaginatedResource


# class that has setUp and tearDown for all transfer client testing classes
class BaseTransferClientTests(CapturedIOTestCase):

    __test__ = False  # prevents base class from trying to run tests

    @classmethod
    def setUpClass(self):
        """
        Does an auth flow to create an authorized client
        """
        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_RT, ac)
        self.tc = globus_sdk.TransferClient(authorizer=authorizer)

    def setUp(self):
        """
        Creates a list for tracking cleanup of assets created during testing
        Sets up a test endpoint
        """
        # list of dicts, each containing a function and a list of args
        # to pass to that function s.t. calling f(*args) cleans an asset
        self.asset_cleanup = []

        # test endpoint, uses 128 bits of randomness to prevent collision
        data = {"display_name": "SDK Test Endpoint-" + str(getrandbits(128)),
                "description": "Endpoint for testing the SDK"}
        r = self.tc.create_endpoint(data)
        self.test_ep_id = r["id"]
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [r["id"]],
                                   "name": "test_ep"})  # for ease of removal

    def tearDown(self):
        """
        Parses created_assets to destroy all assets created during testing
        """
        # call the cleanup functions with the arguments they were given
        for cleanup in self.asset_cleanup:
            cleanup["function"](*cleanup["args"])

    def deleteHelper(self, ep_id, path):
        """
        Helper function for cleanup. Deletes by path and endpoint,
        """
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        ddata = globus_sdk.DeleteData(self.tc, ep_id,
                                      label="deleteHelper",
                                      recursive=True, **kwargs)
        ddata.add_item(path)
        self.tc.submit_delete(ddata)


# class for transfer client tests that don't require time intensive setup
class TransferClientTests(BaseTransferClientTests):

    __test__ = True  # marks sub-class as having tests

    def test_get_endpoint(self):
        """
        Gets endpoint on go#ep1 and go#ep2, validate results
        """

        # load the tutorial endpoint documents
        ep1_doc = self.tc.get_endpoint(GO_EP1_ID)
        ep2_doc = self.tc.get_endpoint(GO_EP2_ID)

        # check that their contents are at least basically sane (i.e. we didn't
        # get empty dicts or something)
        self.assertIn("display_name", ep1_doc)
        self.assertIn("display_name", ep2_doc)
        self.assertIn("canonical_name", ep1_doc)
        self.assertIn("canonical_name", ep2_doc)

        # double check the canonical name fields, consider this done
        self.assertEqual(ep1_doc["canonical_name"], "go#ep1")
        self.assertEqual(ep2_doc["canonical_name"], "go#ep2")

    def test_update_endpoint(self):
        """
        Updates test endpoint, validate results,
        repeats with different update data to confirm data is changing
        """

        # update the test endpoint's display name and description
        # name is randomized to prevent collision
        update_data = {"display_name": "Updated-" + str(getrandbits(128)),
                       "description": "Updated description"}
        update_doc = self.tc.update_endpoint(self.test_ep_id, update_data)

        # make sure response is a successful update
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"],
                         "Endpoint updated successfully")

        # confirm data matches update
        get_doc = self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(get_doc["display_name"], update_data["display_name"])
        self.assertEqual(get_doc["description"], update_data["description"])

        # repeat with different data
        update_data2 = {"display_name": "Updated-" + str(getrandbits(128)),
                        "description": "Updated again description"}
        update_doc2 = self.tc.update_endpoint(self.test_ep_id, update_data2)

        # make sure response is a successful update
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc2["code"], "Updated")
        self.assertEqual(update_doc2["message"],
                         "Endpoint updated successfully")

        # confirm data matches update and changed from previous get
        get_doc2 = self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(get_doc2["display_name"],
                         update_data2["display_name"])
        self.assertEqual(get_doc2["description"], update_data2["description"])

    def test_create_endpoint(self):
        """
        Creates an endpoint, validates results
        """

        # create the endpoint
        create_data = {"display_name": "Test Create-" + str(getrandbits(128))}
        create_doc = self.tc.create_endpoint(create_data)

        # confirm response is a successful creation
        self.assertIn("id", create_doc)
        self.assertEqual(create_doc["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(create_doc["code"], "Created")
        self.assertEqual(create_doc["message"],
                         "Endpoint created successfully")

        # confirm get works on endpoint and returns expected data
        get_doc = self.tc.get_endpoint(create_doc["id"])
        self.assertEqual(get_doc["display_name"], create_data["display_name"])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [create_doc["id"]]})

    def test_delete_endpoint(self):
        """
        Deletes the test endpoint, validates results
        """

        # delete the endpoint
        delete_doc = self.tc.delete_endpoint(self.test_ep_id)

        # confirm response is a successful deletion
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertEqual(delete_doc["message"],
                         "Endpoint deleted successfully")

        # confirm get no longer finds endpoint
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "EndpointDeleted")

        # stop tracking endpoint for cleanup
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_ep":
                self.asset_cleanup.remove(cleanup)
                break

    # def test_endpoint_manager_monitored_endpoints(self):
        # TODO: test against monitored endpoint

    # def test_endpoint_activate(self):
        # TODO: test against an endpoint that uses MyProxy

    def test_endpoint_get_activation_requirements(self):
        """
        Gets activation requirements on tutorial endpoint, validates results
        """

        # get requirements
        reqs_doc = self.tc.endpoint_get_activation_requirements(GO_EP1_ID)

        # confirm doc data type and some expected fields
        self.assertEqual(reqs_doc["DATA_TYPE"], "activation_requirements")
        self.assertIn("activated", reqs_doc)
        self.assertIn("auto_activation_supported", reqs_doc)
        self.assertIn("DATA", reqs_doc)

    def test_my_effective_pause_rule_list(self):
        """
        Gets pause rule list from tutorial endpoint, validates results
        """

        # get the pause list
        pause_doc = self.tc.my_effective_pause_rule_list(GO_EP1_ID)

        # confirm doc data type and that it has the DATA field
        self.assertEqual(pause_doc["DATA_TYPE"], "pause_rule_list")
        self.assertIn("DATA", pause_doc)

    def test_create_shared_endpoint(self):
        """
        Creates a shared endpoint, validates results,
        checks existence and sharing status using get
        """

        # create shared endpoint
        # dir and name are randomized to prevent collision
        share_path = "/~/test_share-" + str(getrandbits(128)) + "/"
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name":
                       "SDK Test Create Shared Endpoint-"
                       + str(getrandbits(128)),
                       }
        share_doc = self.tc.create_shared_endpoint(shared_data)

        # validate share doc
        self.assertEqual(share_doc["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(share_doc["code"], "Created")

        # confirm shared endpoint now exists and is hosted from go#ep1
        get_data = self.tc.get_endpoint(share_doc["id"])
        self.assertEqual(get_data["host_endpoint_id"], GO_EP1_ID)
        self.assertEqual(get_data["sharing_target_root_path"], share_path)

        # track assets for cleanup
        # TODO: track .globus?
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [share_doc["id"]]})
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, share_path]})

    def test_endpoint_server_list(self):
        """
        Gets endpoint server list for go#ep1, validates results
        """

        # get endpoint server list
        list_doc = self.tc.endpoint_server_list(GO_EP1_ID)

        # validate results are a endpoint server list with a DATA field
        self.assertEqual(list_doc["DATA_TYPE"], "endpoint_server_list")
        self.assertIn("DATA", list_doc)
        # validate that data points are servers with an id
        for server in list_doc["DATA"]:
            self.assertEqual(server["DATA_TYPE"], "server")
            self.assertIn("id", server)

    def test_get_endpoint_server(self):
        """
        Gets the go#ep1 server by id, validates results
        """

        # TODO: confirm this value is in-fact constant, then add to constants
        server_id = 207976

        # get a server id from the server list
        get_doc = self.tc.get_endpoint_server(GO_EP1_ID, server_id)

        # validate data_type and the existence of some expected fields
        self.assertEqual(get_doc["DATA_TYPE"], "server")
        self.assertEqual(get_doc["id"], server_id)
        self.assertIn("hostname", get_doc)
        self.assertIn("port", get_doc)

    def test_add_endpoint_server(self):
        """
        Adds a new server with a dummy hostname, validate results
        Returns a server_id for use in testing update and delete
        """

        # add the new server
        add_data = {"hostname": "gridftp.example.org"}
        add_doc = self.tc.add_endpoint_server(self.test_ep_id, add_data)

        # validate results
        self.assertEqual(add_doc["DATA_TYPE"], "endpoint_server_add_result")
        self.assertIn("id", add_doc)
        server_id = add_doc["id"]

        # confirm that get can see the server
        get_doc = self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(get_doc["id"], server_id)
        self.assertEqual(get_doc["hostname"], add_data["hostname"])

        # return server id
        return server_id

    def test_update_endpoint_server(self):
        """
        Adds a new server, updates server data, validates results,
        then confirms get returns the updated data
        """

        # add the new server
        server_id = self.test_add_endpoint_server()

        # update the server's hostname and port
        update_data = {"hostname": "gridftp.updated.org",
                       "port": 2812}
        update_doc = self.tc.update_endpoint_server(self.test_ep_id, server_id,
                                                    update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"], "Server updated successfully")

        # confirm get returns the new data
        get_doc = self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(get_doc["hostname"], update_data["hostname"])
        self.assertEqual(get_doc["port"], update_data["port"])

    def test_delete_endpoint_server(self):
        """
        Adds a new server, deletes it, validates results,
        then confirms get can no longer see the server
        """

        # add the new server
        server_id = self.test_add_endpoint_server()

        # delete the server data
        delete_doc = self.tc.delete_endpoint_server(self.test_ep_id, server_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertEqual(delete_doc["message"], "Server deleted successfully")

        # confirm get can no longer see the server data
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint_server(self.test_ep_id, server_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code,
                         "ClientError.NotFound.ServerNotFound")

    def test_endpoint_role_list(self):
        """
        Gets the endpoint role list from the test endpoint, validates results
        """

        # get endpoint role list
        list_doc = self.tc.endpoint_role_list(self.test_ep_id)

        # validate data type
        self.assertEqual(list_doc["DATA_TYPE"], "role_list")
        self.assertIn("DATA", list_doc)
        # confirm that each role has the expected values
        for role in list_doc["DATA"]:
            self.assertEqual(role["DATA_TYPE"], "role")
            self.assertIn("id", role)
            self.assertIn("principal_type", role)
            self.assertIn("principal", role)
            self.assertIn("role", role)

    def test_add_endpoint_role(self):
        """
        For now, just confirms only managed endpoints can have roles added

        TODO:
        Adds a role to the test endpoint, validates results
        returns role_id for use in get and delete
        """

        # add the new role
        add_data = {"DATA_TYPE": "role",
                    "principal_type": "identity",
                    "principal": GO_USER_ID,
                    "role": "access_manager"
                    }

        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.add_endpoint_role(self.test_ep_id, add_data)
        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "Conflict")

        # TODO: get managed endpoint to test against

        # add_doc = self.tc.add_endpoint_role(self.test_ep_id, add_data)

        # validate results
        # self.assertEqual(add_doc["DATA_TYPE"], "role")
        # self.assertIn("id", add_doc)
        # role_id = add_doc["id"]

        # confirm that get can see the new role
        # get_doc = self.tc.get_endpoint_role(self.test_ep_id, role_id)
        # self.assertEqual(get_doc["id"], role_id)
        # for item in add_data:
        #     self.assertEqual(get_doc[item], add_data[item])

        # return server id
        # return role_id

    def test_get_endpoint_role(self):
        """
        Gets SDK tester's admin role from test_endpoint, validates results
        """

        # TODO: get role_id from add to remove needing the list

        # get role id from role list, assumes admin id is first
        list_doc = self.tc.endpoint_role_list(self.test_ep_id)
        role_id = iter(list_doc["DATA"]).next()["id"]

        # get the role by its id
        get_doc = self.tc.get_endpoint_role(self.test_ep_id, role_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "role")
        self.assertEqual(get_doc["id"], role_id)
        self.assertEqual(get_doc["principal_type"], "identity")
        self.assertEqual(get_doc["principal"], SDK_USER_ID)
        self.assertEqual(get_doc["role"], "administrator")

    def delete_endpoint_role(self, endpoint_id, role_id):
        """
        For now, just confirms only managed endpoints can have roles deleted

        TODO:
        Deletes role from test_endpoint, validates results
        """

        # TODO: get role_id from add, to remove needing the list,
        # and prevent issues that might arise from deleting our own admin role

        # get role id from role list
        list_doc = self.tc.endpoint_role_list(self.test_ep_id)
        role_id = iter(list_doc["DATA"]).next()["id"]

        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.delete_endpoint_role(self.test_ep_id, role_id)
        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "Conflict")

        # TODO: test against managed endpoint

        # delete the role
        # delete_doc = self.tc.delete_endpoint_role(self.test_ep_id, role_id)

        # validate results
        # self.assertEqual(get_doc["DATA_TYPE"], "results")
        # self.assertEqual(get_doc["code"], "Deleted")
        # self.assertIn("deleted successfully", get_doc["message"])

        # confirm get no longer sees the role
        # with self.assertRaises(TransferAPIError) as apiErr:
        #     self.tc.get_endpoint_role(self.test_ep_id, role_id)
        # self.assertEqual(apiErr.exception.http_status, 404)
        # self.assertEqual(apiErr.exception.code, "RoleNotFound")

    def test_bookmark_list(self):
        """
        Gets SDK user's bookmark list, validates results
        """

        # get bookmark list
        list_doc = self.tc.bookmark_list()

        # validate results
        self.assertEqual(list_doc["DATA_TYPE"], "bookmark_list")
        self.assertIn("DATA", list_doc)
        # confirm that each bookmark in the list has expected fields
        for bookmark in list_doc["DATA"]:
            self.assertEqual(bookmark["DATA_TYPE"], "bookmark")
            self.assertIn("id", bookmark)
            self.assertIn("name", bookmark)
            self.assertIn("endpoint_id", bookmark)
            self.assertIn("path", bookmark)

    def test_create_bookmark(self):
        """
        Creates a bookmark, validates results, confirms get sees bookmark,
        returns bookmark_id for use in testing get update and delete
        """

        # create bookmark, name is randomized to prevent collision
        bookmark_data = {"name": "SDK Test Bookmark-" + str(getrandbits(128)),
                         "endpoint_id": GO_EP1_ID,
                         "path": "/~/"}
        create_doc = self.tc.create_bookmark(bookmark_data)

        # validate results
        self.assertEqual(create_doc["DATA_TYPE"], "bookmark")
        self.assertIn("id", create_doc)
        for item in bookmark_data:
            self.assertEqual(create_doc[item], bookmark_data[item])

        # confirm get sees created bookmark
        bookmark_id = create_doc["id"]
        get_doc = self.tc.get_bookmark(bookmark_id)
        self.assertEqual(get_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(get_doc["id"], bookmark_id)
        for item in bookmark_data:
            self.assertEqual(get_doc[item], bookmark_data[item])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.delete_bookmark,
                                   "args": [bookmark_id],
                                   "name": "test_bookmark"})  # for removal

        # return bookmark_id
        return bookmark_id

    def test_get_bookmark(self):
        """
        Creates a bookmark, gets it, validates results
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # get bookmark
        get_doc = self.tc.get_bookmark(bookmark_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(get_doc["id"], bookmark_id)
        self.assertIn("name", get_doc)
        self.assertIn("endpoint_id", get_doc)
        self.assertIn("path", get_doc)

    def test_update_bookmark(self):
        """
        Creates a bookmark, updates it, validates results,
        then confirms get sees the updated data
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # update bookmark name, randomized to prevent collision
        update_data = {"name":
                       "Updated SDK Test Bookmark-" + str(getrandbits(128))}
        update_doc = self.tc.update_bookmark(bookmark_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "bookmark")
        self.assertEqual(update_doc["id"], bookmark_id)
        self.assertEqual(update_doc["name"], update_data["name"])

        # confirm get sees new name
        get_doc = self.tc.get_bookmark(bookmark_id)
        self.assertEqual(get_doc["name"], update_data["name"])

    def test_delete_bookmark(self):
        """
        Creates a bookmark, deletes it, validates results,
        then confirms get no longer sees the bookmark
        """

        # get bookmark from test_create_bookmark
        bookmark_id = self.test_create_bookmark()

        # delete bookmark
        delete_doc = self.tc.delete_bookmark(bookmark_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertIn("deleted successfully", delete_doc["message"])

        # confirm get no longer sees bookmark
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_bookmark(bookmark_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "BookmarkNotFound")

        # stop tracking asset for deletion
        for cleanup in self.asset_cleanup:
            if "name" in cleanup and cleanup["name"] == "test_bookmark":
                self.asset_cleanup.remove(cleanup)
                break

    def test_operation_ls(self):
        """
        Performs ls operations on go#ep1, tests path, show_hidden, limit,
        and filter params, validates results and confirms behavior,
        """

        # perform ls operation without params
        ls_doc = self.tc.operation_ls(GO_EP1_ID)
        # validate results
        self.assertEqual(ls_doc["DATA_TYPE"], "file_list")
        self.assertEqual(ls_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(ls_doc["path"], "/~/")  # default path
        self.assertIn("DATA", ls_doc)

        # perform ls operation with path param
        path = "/share/godata/"
        path_params = {"path": path}
        path_doc = self.tc.operation_ls(GO_EP1_ID, **path_params)
        # validate results
        self.assertEqual(path_doc["DATA_TYPE"], "file_list")
        self.assertEqual(path_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(path_doc["path"], path)
        self.assertIn("DATA", path_doc)
        # confirm the three text files are found as expected
        for item in path_doc["DATA"]:
            self.assertEqual(item["DATA_TYPE"], "file")
            self.assertIn(".txt", item["name"])
            self.assertIn("size", item)
            self.assertIn("permissions", item)

        # perform ls operation show_hidden param set to false
        hidden_params = {"show_hidden": False}
        hidden_doc = self.tc.operation_ls(GO_EP1_ID, **hidden_params)
        # validate results
        self.assertEqual(hidden_doc["DATA_TYPE"], "file_list")
        self.assertEqual(hidden_doc["endpoint"], GO_EP1_ID)
        self.assertIn("DATA", hidden_doc)
        # confirm no hidden files were returned
        for item in hidden_doc["DATA"]:
            self.assertFalse(item["name"][0] == ".")

        # perform ls operation with limit param
        limit = 1
        limit_params = {"path": path, "limit": limit}
        limit_doc = self.tc.operation_ls(GO_EP1_ID, **limit_params)
        # validate results
        self.assertEqual(limit_doc["DATA_TYPE"], "file_list")
        self.assertEqual(limit_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(limit_doc["path"], path)
        # confirm only one of the three files was returned
        self.assertEqual(limit_doc["length"], limit)
        file_count = 0
        for item in limit_doc:
            file_count += 1
        self.assertEqual(file_count, limit)

        # perform ls operation with filter param
        file_name = "file3.txt"
        min_size = 5
        filter_string = "name:" + file_name + "/size:>" + str(min_size)
        filter_params = {"filter": filter_string, "path": path}
        filter_doc = self.tc.operation_ls(GO_EP1_ID, **filter_params)
        # validate results
        self.assertEqual(filter_doc["DATA_TYPE"], "file_list")
        self.assertEqual(filter_doc["endpoint"], GO_EP1_ID)
        self.assertEqual(filter_doc["path"], path)
        # confirm only file 3 was returned
        file_data = iter(filter_doc["DATA"]).next()
        self.assertEqual(file_data["name"], file_name)
        self.assertTrue(file_data["size"] > min_size)

    def test_operation_mkdir(self):
        """
        Performs mkdir operation in go#ep1/~/, validates results,
        confirms ls sees the new directory
        """

        # perform mkdir operation, name randomized to prevent collision
        dir_name = "test_dir-" + str(getrandbits(128))
        path = "/~/" + dir_name
        mkdir_doc = self.tc.operation_mkdir(GO_EP1_ID, path)

        # validate results
        self.assertEqual(mkdir_doc["DATA_TYPE"], "mkdir_result")
        self.assertEqual(mkdir_doc["code"], "DirectoryCreated")
        self.assertEqual(mkdir_doc["message"],
                         "The directory was created successfully")

        # confirm ls now sees the dir
        filter_string = "name:" + dir_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertNotEqual(ls_doc["DATA"], [])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, path]})

    def test_operation_rename(self):
        """
        Performs mkdir operation, renames the directory,
        confirms ls sees the new directory and not the old one.
        """

        # perform mkdir operation, name randomized to prevent collision
        old_name = "old_dir-" + str(getrandbits(128))
        old_path = "/~/" + old_name
        self.tc.operation_mkdir(GO_EP1_ID, old_path)

        # rename the directory, name randomized to prevent collision
        new_name = "new_dir-" + str(getrandbits(128))
        new_path = "/~/" + new_name
        rename_doc = self.tc.operation_rename(GO_EP1_ID, old_path, new_path)

        # validate results
        self.assertEqual(rename_doc["DATA_TYPE"], "result")
        self.assertEqual(rename_doc["code"], "FileRenamed")
        self.assertEqual(rename_doc["message"],
                         "File or directory renamed successfully")

        # confirm ls sees new directory
        filter_string = "name:" + new_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertNotEqual(ls_doc["DATA"], [])

        # confirm ls does not see old directory
        filter_string = "name:" + old_name
        params = {"filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(ls_doc["DATA"], [])

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, new_path]})

    def test_operation_get_submission_id(self):
        """
        Gets a submission_id, validates results, checks UUID looks reasonable
        """

        # get submission id
        sub_doc = self.tc.get_submission_id()

        # validate results
        self.assertEqual(sub_doc["DATA_TYPE"], "submission_id")
        self.assertIn("value", sub_doc)

        # check that the UUID is in the right format
        uuid = sub_doc["value"]
        self.assertEqual(len(uuid), 36)
        self.assertEqual(uuid[8], "-")
        self.assertEqual(uuid[13], "-")
        self.assertEqual(uuid[18], "-")
        self.assertEqual(uuid[23], "-")

    def test_submit_transfer(self):
        """
        Submits transfer requests, validates results, confirms tasks completed
        tests recursive and submission_id parameters
        """

        # dir for testing transfers in, name randomized to prevent collision
        dest_dir = "transfer_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # individual file and recursive dir transfer
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        # individual
        file_name = "file1.txt"
        dir_name = "godata"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        # recursive into a new data dir
        tdata.add_item(source_path, dest_path + dir_name, recursive=True)
        # send the request
        transfer_doc = self.tc.submit_transfer(tdata)

        # validate results
        self.assertEqual(transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(transfer_doc["code"], "Accepted")
        self.assertIn("task_id", transfer_doc)
        self.assertIn("submission_id", transfer_doc)

        # confirm the task completed and the files were transfered
        task_id = transfer_doc["task_id"]
        self.assertTrue(
            self.tc.task_wait(task_id, timeout=30, polling_interval=1))
        # confirm file and dir are visible by ls
        filter_string = "name:" + file_name + "," + dir_name
        params = {"path": dest_path, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(len(ls_doc["DATA"]), 2)
        # confirm 3 .txt files are found in dir
        filter_string = "name:~*.txt"
        params = {"path": dest_path + dir_name, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(len(ls_doc["DATA"]), 3)

        # test submission_id parameter
        sub_id = self.tc.get_submission_id()["value"]

        # confirm first submission is normal
        sub_tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID, GO_EP1_ID,
                                            submission_id=sub_id, **kwargs)
        sub_tdata.add_item(source_path + file_name, dest_path + file_name)
        sub_transfer_doc = self.tc.submit_transfer(sub_tdata)
        # validate results
        self.assertEqual(sub_transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(sub_transfer_doc["code"], "Accepted")
        self.assertEqual(sub_transfer_doc["submission_id"], sub_id)
        self.assertIn("task_id", sub_transfer_doc)
        sub_task_id = sub_transfer_doc["task_id"]

        # confirm re-using submission_id returns a Duplicate response
        resub_tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID, GO_EP1_ID,
                                              submission_id=sub_id, **kwargs)
        resub_tdata.add_item(source_path + file_name, dest_path + file_name)
        resub_transfer_doc = self.tc.submit_transfer(resub_tdata)
        self.assertEqual(resub_transfer_doc["DATA_TYPE"], "transfer_result")
        self.assertEqual(resub_transfer_doc["code"], "Duplicate")
        self.assertEqual(resub_transfer_doc["submission_id"], sub_id)
        self.assertEqual(resub_transfer_doc["task_id"], sub_task_id)

        # wait for submission to finish before moving on to cleanup
        self.assertTrue(self.tc.task_wait(sub_transfer_doc["task_id"],
                                          timeout=30, polling_interval=1))

    def test_submit_delete(self):
        """
        Transfers a file and makes a dir in go#ep1, then deletes them,
        validates results and that the items are no longer visible by ls
        Confirms resubmission using the same data returns a Duplicate response
        """

        # dir for testing deletes in, name randomized to prevent collision
        dest_dir = "delete_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # transfer file into go#ep1/~/dir_name
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)

        # make a dir to delete
        dir_name = "test_dir"
        path = dest_path + dir_name
        self.tc.operation_mkdir(GO_EP1_ID, path)

        # wait for transfer to complete
        self.assertTrue(self.tc.task_wait(transfer_doc["task_id"],
                                          timeout=30, polling_interval=1))

        # delete the items
        ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID,
                                      recursive=True, **kwargs)
        ddata.add_item(dest_path + file_name)
        ddata.add_item(dest_path + dir_name)
        delete_doc = self.tc.submit_delete(ddata)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "delete_result")
        self.assertEqual(delete_doc["code"], "Accepted")
        self.assertIn("task_id", delete_doc)
        self.assertIn("submission_id", delete_doc)
        task_id = delete_doc["task_id"]
        sub_id = delete_doc["submission_id"]

        # confirm the task completed and the files were deleted
        # wait for transfer to complete
        self.assertTrue(self.tc.task_wait(task_id, timeout=30,
                                          polling_interval=1))
        # confirm file and dir are no longer visible by ls
        filter_string = "name:" + file_name + "," + dir_name
        params = {"path": dest_path, "filter": filter_string}
        ls_doc = self.tc.operation_ls(GO_EP1_ID, **params)
        self.assertEqual(ls_doc["DATA"], [])

        # confirm re-submission of ddata returns Duplicate response
        resub_delete_doc = self.tc.submit_delete(ddata)
        self.assertEqual(resub_delete_doc["DATA_TYPE"], "delete_result")
        self.assertEqual(resub_delete_doc["code"], "Duplicate")
        self.assertEqual(resub_delete_doc["submission_id"], sub_id)
        self.assertEqual(resub_delete_doc["task_id"], task_id)

    # def test_def endpoint_manager_task_list(self):
        # TODO: give SDK test activity_monitor role on an endpoint

    def test_task_list(self):
        """
        Gets task list, validates results, tests num_results and filter params
        """

        # get task list
        list_doc = self.tc.task_list()

        # validate results are in the right format
        self.assertIsInstance(list_doc, PaginatedResource)
        # validate tasks have some expected fields
        for task in list_doc:
            self.assertEqual(task["DATA_TYPE"], "task")
            self.assertEqual(task["owner_id"], SDK_USER_ID)
            self.assertIn("task_id", task)
            self.assertIn("type", task)
            self.assertIn("status", task)

        # test num_results param, assumes SDK tester has run at least 20 tasks
        cap = 20
        num_doc = self.tc.task_list(num_results=cap)
        # confirm results were capped
        count = 0
        for task in num_doc:
            count += 1
        self.assertEqual(count, cap)

        # test filter param
        params = {"filter": "type:DELETE/status:SUCCEEDED"}
        filter_doc = self.tc.task_list(**params)
        # validate only Successful Delete tasks were returned
        for task in filter_doc:
            self.assertEqual(task["type"], "DELETE")
            self.assertEqual(task["status"], "SUCCEEDED")

    def test_task_event_list(self):
        """
        Gets the task event list for a completed transfer,
        validates results, tests filter param
        """

        # get the task event list for a completed transfer
        task_id = self.test_get_task()
        list_doc = self.tc.task_event_list(task_id)

        # validate results
        self.assertIsInstance(list_doc, PaginatedResource)
        for event in list_doc:
            self.assertEqual(event["DATA_TYPE"], "event")
            self.assertIn("is_error", event)
            self.assertIn("code", event)
            self.assertIn("time", event)

        # test filter param
        params = {"filter": "is_error:1"}
        filter_doc = self.tc.task_event_list(task_id, **params)
        for event in filter_doc:
            self.assertEqual(event["is_error"], True)

    def test_get_task(self):
        """
        Submits a transfer, waits for transfer to complete, gets transfer task
        validates results
        returns the task_id for use in other test functions
        """

        # dir the test transfer, name randomized to prevent collision
        dest_dir = "get_task_dest_dir-" + str(getrandbits(128))
        dest_path = "/~/" + dest_dir + "/"
        self.tc.operation_mkdir(GO_EP1_ID, dest_path)
        # track asset for cleanup
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, dest_path]})

        # submit transfer task
        source_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)

        # wait for task to complete
        task_id = transfer_doc["task_id"]
        self.assertTrue(self.tc.task_wait(task_id, timeout=30,
                                          polling_interval=1))

        # get the task by id
        get_doc = self.tc.get_task(task_id)
        self.assertEqual(get_doc["DATA_TYPE"], "task")
        self.assertEqual(get_doc["task_id"], task_id)
        self.assertEqual(get_doc["owner_id"], SDK_USER_ID)
        self.assertEqual(get_doc["type"], "TRANSFER")
        self.assertIn("status", get_doc)

        # return task_id
        return task_id

    def test_update_task(self):
        """
        Submits an un-allowed transfer task, updates task, validates results,
        confirms a conflict error when trying to update a completed task
        """

        # submit an un-allowed transfer task
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        task_id = transfer_doc["task_id"]

        # update task, deadline is in the past for automatic cleanup
        update_data = {"DATA_TYPE": "task", "label": "updated",
                       "deadline": "2000-01-01 00:00:06+00:00"}
        update_doc = self.tc.update_task(task_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertEqual(update_doc["message"],
                         "Updated task deadline and label successfully")

        # confirm a conflict error when updating a completed task
        completed_id = self.test_get_task()
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.update_task(completed_id, update_data)
        self.assertEqual(apiErr.exception.http_status, 409)
        self.assertEqual(apiErr.exception.code, "Conflict")

    def test_cancel_task(self):
        """
        Submits an un-allowed transfer task, cancels task, validates results,
        confirms a complete task is seen as such and returns correct code
        """

        # submit an un-allowed transfer task
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        task_id = transfer_doc["task_id"]

        # cancel task
        cancel_doc = self.tc.cancel_task(task_id)

        # validate results
        self.assertEqual(cancel_doc["DATA_TYPE"], "result")
        self.assertEqual(cancel_doc["code"], "Canceled")
        self.assertEqual(cancel_doc["message"],
                         "The task has been cancelled successfully.")

        # confirm a conflict error when updating a completed task
        complete_id = self.test_get_task()
        complete_doc = self.tc.cancel_task(complete_id)
        self.assertEqual(complete_doc["DATA_TYPE"], "result")
        self.assertEqual(complete_doc["code"], "TaskComplete")
        self.assertEqual(
            complete_doc["message"],
            "The task completed before the cancel request was processed.")

    def test_task_wait(self):
        """
        Waits on complete, and never completing tasks, confirms results
        """

        # complete
        complete_id = self.test_get_task()
        self.assertTrue(self.tc.task_wait(complete_id, timeout=1))

        # never completing
        source_path = "/share/godata/"
        dest_path = "/share/godata/"
        kwargs = {"notify_on_succeeded": False, "notify_on_fail": False,
                  "notify_on_inactive": False}  # prevent email spam
        tdata = globus_sdk.TransferData(self.tc, GO_EP2_ID,
                                        GO_EP1_ID, **kwargs)
        file_name = "file1.txt"
        tdata.add_item(source_path + file_name, dest_path + file_name)
        transfer_doc = self.tc.submit_transfer(tdata)
        never_id = transfer_doc["task_id"]

        self.assertFalse(self.tc.task_wait(never_id, timeout=1))

        # track asset for cleanup
        self.asset_cleanup.append({"function": self.tc.cancel_task,
                                   "args": [never_id]})

    def test_task_pause_info(self):
        """
        Gets the pause info for a task, validates results
        """

        # get pause info
        task_id = self.test_get_task()
        pause_doc = self.tc.task_pause_info(task_id)

        # validate results
        self.assertEqual(pause_doc["DATA_TYPE"], "pause_info_limited")
        self.assertIsNone(pause_doc["source_pause_message"])
        self.assertIsNone(pause_doc["destination_pause_message"])
        self.assertIn("pause_rules", pause_doc)

        # TODO: test against an endpoint with pause rules

    def test_task_successful_transfers(self):
        """
        Gets the successful transfers from a completed task, validates results
        """

        # get successful transfer info
        task_id = self.test_get_task()
        transfers_doc = self.tc.task_successful_transfers(task_id)

        # validate results
        self.assertIsInstance(transfers_doc, PaginatedResource)
        for success in transfers_doc:
            self.assertEqual(success["DATA_TYPE"], "successful_transfer")
            self.assertIn("source_path", success)
            self.assertIn("destination_path", success)


# class for Transfer Client Tests that require a shared endpoint
# since tearDown takes significantly longer if a shared endpoint was made
class SharedTransferClientTests(BaseTransferClientTests):

    __test__ = True  # marks sub-class as having tests

    def setUp(self):
        """
        calls BaseTransferClientTest setUp,
        then sets up a test shared endpoint
        """
        super(SharedTransferClientTests, self).setUp()

        # shared endpoint hosted on go#ep1,
        # name and dir randomized to prevent collision
        share_path = "/~/share-" + str(getrandbits(128))
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name":
                       "SDK Test Shared Endpoint-" + str(getrandbits(128)),
                       "description": "Shared Endpoint for testing the SDK"
                       }
        r = self.tc.create_shared_endpoint(shared_data)
        self.test_share_ep_id = r["id"]

        # track assets for cleanup
        # TODO: track .globus?
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [r["id"]]})
        self.asset_cleanup.append({"function": self.deleteHelper,
                                   "args": [GO_EP1_ID, share_path]})

    def test_endpoint_search(self):
        """
        Searches by fulltext, owner_id, and scopes, validates results
        """

        # full-text and cap of num_results
        search_string = "tutorial"
        cap = 5
        text_doc = self.tc.endpoint_search(search_string, num_results=cap)
        # confirm the results are in the right format, are capped correctly,
        # and that the results have the search string in their display names
        self.assertIsInstance(text_doc, PaginatedResource)
        results_count = 0
        for ep in text_doc:
            self.assertIn(search_string, str.lower(str(ep["display_name"])))
            results_count += 1
        self.assertEqual(results_count, cap)

        # owner-id param
        params = {"filter_owner_id": GO_USER_ID}
        owner_doc = self.tc.endpoint_search(**params)
        # confirm format, and that all results are from GO
        self.assertIsInstance(owner_doc, PaginatedResource)
        for ep in owner_doc:
            self.assertEqual(ep["owner_id"], GO_USER_ID)

        # scope: my endpoints
        my_doc = self.tc.endpoint_search(filter_scope="my-endpoints")
        # confirm format, and that all results are owned by SDK tester
        self.assertIsInstance(my_doc, PaginatedResource)
        for ep in my_doc:
            self.assertEqual(ep["owner_id"], SDK_USER_ID)

        # scope: shared endpoints
        my_doc = self.tc.endpoint_search(filter_scope="shared-by-me")
        # confirm format, and that all results are shared by SDK tester
        self.assertIsInstance(my_doc, PaginatedResource)
        for ep in my_doc:
            self.assertEqual(ep["owner_id"], SDK_USER_ID)
            self.assertIsNotNone(ep["sharing_target_root_path"])
            self.assertIsNotNone(ep["host_endpoint_id"])

    def test_endpoint_autoactivate(self):
        """
        Deactivates, then auto-activates shared endpoint,
        confirms activation through get,
        confirms trying again with if_expires_in returns AlreadyActivated
        """

        # deactivate
        self.tc.endpoint_deactivate(self.test_share_ep_id)

        # auto-activate and check for successful response code

        auto_doc = self.tc.endpoint_autoactivate(self.test_share_ep_id)
        self.assertEqual(auto_doc["code"],
                         "AutoActivated.GlobusOnlineCredential")

        # confirm get sees the endpoint as activated now
        get_doc = self.tc.get_endpoint(self.test_share_ep_id)
        self.assertTrue(get_doc["activated"])

        # confirm if_expires_in sees the endpoint as activated
        params = {"if_expires_in": "60"}
        expires_doc = self.tc.endpoint_autoactivate(
            self.test_share_ep_id, **params)
        self.assertEqual(expires_doc["code"], "AlreadyActivated")

        # TODO: test against an endpoint we are not allowed to activate

    def test_endpoint_deactivate(self):
        """
        Auto-activates, then deactivates shared endpoint,
        confirms deactivation through get
        """

        # activate
        self.tc.endpoint_autoactivate(self.test_share_ep_id)

        # deactivate and check for successful response code
        deact_doc = self.tc.endpoint_deactivate(self.test_share_ep_id)
        self.assertEqual(deact_doc["code"], "Deactivated")

        # confirm get sees the endpoint as deactivated now
        get_doc = self.tc.get_endpoint(self.test_share_ep_id)
        self.assertFalse(get_doc["activated"])

    def test_my_shared_endpoint_list(self):
        """
        Gets my shared endpoint list, validates results
        """

        # get shared endpoint list
        share_doc = self.tc.my_shared_endpoint_list(GO_EP1_ID)

        # confirm doc type, and that test_share_ep_id is on the list
        self.assertEqual(share_doc["DATA_TYPE"], "endpoint_list")
        share_test_found = False
        for ep in share_doc:
            share_test_found = (ep["id"] == self.test_share_ep_id
                                or share_test_found)
        self.assertTrue(share_test_found)

    def test_endpoint_acl_list(self):
        """
        Gets endpoint access rule list from test_share_ep, validates results
        """

        # get endpoint role list
        list_doc = self.tc.endpoint_acl_list(self.test_share_ep_id)

        # validate responce has been put into
        self.assertEqual(list_doc["DATA_TYPE"], "access_list")
        self.assertIn("DATA", list_doc)
        # confirm that each access rule has some expected values
        for access in list_doc["DATA"]:
            self.assertEqual(access["DATA_TYPE"], "access")
            self.assertIn("id", access)
            self.assertIn("principal_type", access)
            self.assertIn("principal", access)
            self.assertIn("permissions", access)

    def test_get_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, gets it by id, validates results
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # get the access rule by id
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)

        # validate results
        self.assertEqual(get_doc["DATA_TYPE"], "access")
        self.assertEqual(get_doc["id"], access_id)

    def test_add_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, validates results,
        then confirms get sees the new access rule,
        returns the access_id for use in testing get update and delete
        """

        # add root read access to all users logged in with auth
        add_data = {"DATA_TYPE": "access",
                    "principal_type": "all_authenticated_users",
                    "principal": "",
                    "path": "/",
                    "permissions": "r"
                    }
        add_doc = self.tc.add_endpoint_acl_rule(self.test_share_ep_id,
                                                add_data)

        # validate results
        self.assertEqual(add_doc["DATA_TYPE"], "access_create_result")
        self.assertEqual(add_doc["code"], "Created")
        self.assertEqual(add_doc["message"],
                         "Access rule created successfully.")
        self.assertIn("access_id", add_doc)

        # confirm get sees new access rule
        access_id = add_doc["access_id"]
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)
        self.assertEqual(get_doc["id"], access_id)
        for item in add_data:
            self.assertEqual(get_doc[item], add_data[item])

        # return access_id
        return access_id

    def test_update_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, updates that access rule,
        validates results, then confirms get sees the new changes
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # update the access rule by id
        update_data = {"permissions": "rw"}
        update_doc = self.tc.update_endpoint_acl_rule(self.test_share_ep_id,
                                                      access_id, update_data)

        # validate results
        self.assertEqual(update_doc["DATA_TYPE"], "result")
        self.assertEqual(update_doc["code"], "Updated")
        self.assertIn("permissions updated successfully",
                      update_doc["message"])

        # confirm get sees new permissions
        get_doc = self.tc.get_endpoint_acl_rule(self.test_share_ep_id,
                                                access_id)
        self.assertEqual(get_doc["permissions"], update_data["permissions"])

    def test_delete_endpoint_acl_rule(self):
        """
        Adds access rule to test_share_ep, deletes that access rule,
        validates results, then confirms get no longer sees the access rule
        """

        # get access rule id through test_add_endpoint_acl_rule
        access_id = self.test_add_endpoint_acl_rule()

        # delete the access rule by id
        delete_doc = self.tc.delete_endpoint_acl_rule(self.test_share_ep_id,
                                                      access_id)

        # validate results
        self.assertEqual(delete_doc["DATA_TYPE"], "result")
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertIn("deleted successfully", delete_doc["message"])

        # confirm get no longer sees the access rule
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint_acl_rule(self.test_share_ep_id, access_id)
        self.assertEqual(apiErr.exception.http_status, 404)
        self.assertEqual(apiErr.exception.code, "AccessRuleNotFound")
