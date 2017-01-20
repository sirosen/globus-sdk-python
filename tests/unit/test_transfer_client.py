import globus_sdk

from tests.framework import (
    CapturedIOTestCase, get_client_data,
    GO_EP1_ID, GO_EP2_ID, SDKTESTER1A_NATIVE1_RT)
from globus_sdk.exc import TransferAPIError


class TransferClientTests(CapturedIOTestCase):

    def clean(self):
        """
        deletes all endpoints managed by SDK Tester
        deletes all files and folders in SDK Tester's home directory
        on both go#ep1 and go#ep2
        """
        r = self.tc.endpoint_search(filter_scope="my-endpoints")
        for ep in r:
            print "DELETING: ", ep["id"],
            self.tc.delete_endpoint(ep["id"])

        # TODO: Clean home directories

    def setUp(self):
        """
        does an auth flow to create an authorized client
        calls clean to prevent colisions with pre-exisiting data
        sets up a test endpoint
        """
        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_RT, ac)
        self.tc = globus_sdk.TransferClient(authorizer=authorizer)

        self.clean()

        r = self.tc.create_endpoint({"display_name": "SDK Test Endpoint"})
        self.test_ep_id = r["id"]

    def tearDown(self):
        """
        calls clean to remove any data created in setUp or individual tests
        """
        self.clean()
        # TODO: should SDK Tester log out here?

    def test_get_endpoint(self):
        """
        Get endpoint on go#ep1 and go#ep2, validate results
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
        Update test endpoint, validate results
        Repeat with different update data to confirm data is changing
        """

        # update the test endpoint's display name and description
        update_data = {"display_name": "Updated display_name",
                       "description": "Updated description"}
        update_doc = self.tc.update_endpoint(self.test_ep_id, update_data)

        # make sure responce is a successfull update
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

        # make sure responce is a successfull update
        self.assertEqual(update_doc2["code"], "Updated")
        self.assertEqual(update_doc2["message"],
                         "Endpoint updated successfully")

        # confirm data matches update and changed from preivous get
        get_doc2 = self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(get_doc2["display_name"],
                         update_data2["display_name"])
        self.assertEqual(get_doc2["description"], update_data2["description"])

    def test_create_endpoint(self):
        """
        Create an endpoint, validate results
        """

        # create the endpoint
        create_data = {"display_name": "Test Create"}
        create_doc = self.tc.create_endpoint(create_data)

        # confirm responce is a successfull creation
        self.assertIn("id", create_doc)
        self.assertEqual(create_doc["code"], "Created")
        self.assertEqual(create_doc["message"],
                         "Endpoint created successfully")

        # confirm get works on endpoint and returns expected data
        get_doc = self.tc.get_endpoint(create_doc['id'])
        self.assertEqual(get_doc["display_name"], create_data["display_name"])

    def test_delete_endpoint(self):
        """
        Delete the test endpoint, validate results
        """

        # delete the endpoint
        delete_doc = self.tc.delete_endpoint(self.test_ep_id)

        # confirm response is a successfull deletion
        self.assertEqual(delete_doc["code"], "Deleted")
        self.assertEqual(delete_doc["message"],
                         "Endpoint deleted successfully")

        # confirm get no longer finds enpdoint
        with self.assertRaises(TransferAPIError) as apiErr:
            self.tc.get_endpoint(self.test_ep_id)
        self.assertEqual(apiErr.exception[0], 404)
        self.assertEqual(apiErr.exception[1], "EndpointDeleted")
