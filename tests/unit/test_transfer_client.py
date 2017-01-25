import globus_sdk

from tests.framework import (CapturedIOTestCase, get_client_data,
                             GO_EP1_ID, GO_EP2_ID,
                             GO_USER_ID, SDK_USER_ID,
                             SDKTESTER1A_NATIVE1_RT)
from globus_sdk.exc import TransferAPIError
from globus_sdk.transfer.paging import PaginatedResource


class TransferClientTests(CapturedIOTestCase):

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

    def clean(self):
        """
        Deletes all endpoints owned by SDK Tester
        deletes all files and folders in SDK Tester's home directory
        on both go#ep1 and go#ep2
        """
        # clean SDK Tester's home /~/ on go#ep1 and go#ep2
        ep_ids = [GO_EP1_ID, GO_EP2_ID]
        task_ids = []
        for ep_id in ep_ids:
            ddata = globus_sdk.DeleteData(self.tc, ep_id, recursive=True)
            r = self.tc.operation_ls(ep_id)
            for item in r:
                ddata.add_item("/~/" + item["name"])
            if len(ddata["DATA"]):
                r = self.tc.submit_delete(ddata)
                task_ids.append(r["task_id"])

        # clean endpoints owned by SDK Tester
        r = self.tc.endpoint_search(filter_scope="my-endpoints")
        for ep in r:
            self.tc.delete_endpoint(ep["id"])

        # wait for deletes to complete
        for task_id in task_ids:
            self.tc.task_wait(task_id, polling_interval=1)

    def setUp(self):
        """
        Calls clean to prevent collisions with pre-existing data,
        sets up a non shared test endpoint,
        sets up a test shared endpoint
        """
        self.clean()

        # non shared endpoint
        data = {"display_name": "SDK Test Endpoint",
                "description": "Endpoint for testing the SDK"}
        r = self.tc.create_endpoint(data)
        self.test_ep_id = r["id"]

        # TODO: move shared endpoint tests to another class
        # to save time for tests that don't need this

        # shared endpoint hosted on go#ep1
        share_path = "/~/share"
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name": "SDK Test Shared Endpoint",
                       "description": "Shared Endpoint for testing the SDK"
                       }
        r = self.tc.create_shared_endpoint(shared_data)
        self.test_share_ep_id = r["id"]

    def tearDown(self):
        """
        Calls clean to remove any data created in setUp or testing
        """
        self.clean()

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
        update_data = {"display_name": "Updated display_name",
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
        update_data2 = {"display_name": "Updated again display_name",
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
        create_data = {"display_name": "Test Create"}
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

    # def test_endpoint_manager_monitored_endpoints(self):
        # TODO: test against monitored endpoint

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
        Deactivates, then auto-activates tutorial endpoint,
        confirms activation through get,
        confirms trying again with if_expires_in returns AlreadyActivated
        """

        # deactivate
        self.tc.endpoint_deactivate(GO_EP1_ID)

        # auto-activate and check for successful response code
        auto_doc = self.tc.endpoint_autoactivate(GO_EP1_ID)
        self.assertEqual(auto_doc["code"],
                         "AutoActivated.GlobusOnlineCredential")

        # confirm get sees the endpoint as activated now
        get_doc = self.tc.get_endpoint(GO_EP1_ID)
        self.assertTrue(get_doc["activated"])

        # confirm if_expires_in sees the endpoint as activated
        params = {"if_expires_in": "60"}
        expires_doc = self.tc.endpoint_autoactivate(GO_EP1_ID, **params)
        self.assertEqual(expires_doc["code"], "AlreadyActivated")

        # TODO: test against an endpoint we are not allowed to activate

    def test_endpoint_deactivate(self):
        """
        Auto-activates, then deactivates tutorial endpoint,
        confirms deactivation through get
        """

        # activate
        self.tc.endpoint_autoactivate(GO_EP1_ID)

        # deactivate and check for successful response code
        deact_doc = self.tc.endpoint_deactivate(GO_EP1_ID)
        self.assertEqual(deact_doc["code"], "Deactivated")

        # confirm get sees the endpoint as activated now
        get_doc = self.tc.get_endpoint(GO_EP1_ID)
        self.assertFalse(get_doc["activated"])

    # def test_endpoint_activate(self):
        # TODO: test against an endpoint that uses MyProxy instead of OAuth2

    def test_endpoint_get_activation_requirements(self):
        """
        Gets activation requirements on tutorial endpoint, validate results
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
            share_test_found = (ep["id"] == self.test_share_ep_id)
        self.assertTrue(share_test_found)

    def test_create_shared_endpoint(self):
        """
        Creates a shared endpoint, validates results,
        checks existence and sharing status using get
        """

        # create shared endpoint
        share_path = "/~/test_share/"
        self.tc.operation_mkdir(GO_EP1_ID, path=share_path)
        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": share_path,
                       "display_name": "SDK Test Create Shared Endpoint",
                       }
        share_doc = self.tc.create_shared_endpoint(shared_data)

        # validate share doc
        self.assertEqual(share_doc["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(share_doc["code"], "Created")

        # confirm shared endpoint now exists and is hosted from go#ep1
        get_data = self.tc.get_endpoint(share_doc["id"])
        self.assertEqual(get_data["host_endpoint_id"], GO_EP1_ID)
        self.assertEqual(get_data["sharing_target_root_path"], share_path)

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

        Goal:
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

    # def delete_endpoint_role(self, endpoint_id, role_id):
        """
        For now, just confirms only managed endpoints can have roles deleted

        Goal:
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

    def test_endpoint_acl_list(self):
        """
        Gets endpoint access rule list from test_ep, validates results
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
