import globus_sdk

from tests.framework import (CapturedIOTestCase, get_client_data,
                             SDKTESTER1A_NATIVE1_RT,
                             GO_EP1_ID, GO_EP2_ID)


class DataTests(CapturedIOTestCase):

    def setUp(self):
        """
        Creates two TransferData objects and two Delete objects for testing,
        one with defaults and one with custom paramaters

        """
        super(DataTests, self).setUp()

        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_RT, ac)
        self.tc = globus_sdk.TransferClient(authorizer=authorizer)

        # constants
        self.label = "label"
        self.params = {"param1": "value1", "param2": "value2"}

        # default transfer data
        self.tdata = globus_sdk.TransferData(self.tc, GO_EP1_ID, GO_EP2_ID)
        # transfer data with paramaters
        self.param_tdata = globus_sdk.TransferData(self.tc,
                                                   GO_EP1_ID, GO_EP2_ID,
                                                   label=self.label,
                                                   sync_level="exists",
                                                   **self.params)
        # default delete data
        self.ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID)
        # delete data with paramaters
        self.param_ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID,
                                                 label=self.label,
                                                 recursive="True",
                                                 **self.params)

    def test_tranfer_init(self):
        """
        Verifies TransferData field initialization
        """

        # default init
        self.assertEqual(self.tdata["DATA_TYPE"], "transfer")
        self.assertEqual(self.tdata["source_endpoint"], GO_EP1_ID)
        self.assertEqual(self.tdata["destination_endpoint"], GO_EP2_ID)
        self.assertIn("submission_id", self.tdata)
        self.assertIn("DATA", self.tdata)
        self.assertEqual(len(self.tdata["DATA"]), 0)

        # init with params
        self.assertEqual(self.param_tdata["label"], self.label)
        # sync_level of "exists" should be converted to 0
        self.assertEqual(self.param_tdata["sync_level"], 0)
        for par in self.params:
            self.assertEqual(self.param_tdata[par], self.params[par])

    def test_transfer_add_item(self):
        """
        Adds two items to TransferData, verifies results
        """
        # add item
        source_path = "source/path/"
        dest_path = "dest/path/"
        self.tdata.add_item(source_path, dest_path)
        # verify results
        self.assertEqual(len(self.tdata["DATA"]), 1)
        data = self.tdata["DATA"][0]
        self.assertEqual(data["DATA_TYPE"], "transfer_item")
        self.assertEqual(data["source_path"], source_path)
        self.assertEqual(data["destination_path"], dest_path)
        self.assertEqual(data["recursive"], False)

        # add recursive item
        self.tdata.add_item(source_path, dest_path, recursive=True)
        # verify results
        self.assertEqual(len(self.tdata["DATA"]), 2)
        r_data = self.tdata["DATA"][1]
        self.assertEqual(r_data["DATA_TYPE"], "transfer_item")
        self.assertEqual(r_data["source_path"], source_path)
        self.assertEqual(r_data["destination_path"], dest_path)
        self.assertEqual(r_data["recursive"], True)

    def test_delete_init(self):
        """
        Verifies DeleteData field initialization
        """

        # default init
        self.assertEqual(self.ddata["DATA_TYPE"], "delete")
        self.assertEqual(self.ddata["endpoint"], GO_EP1_ID)
        self.assertIn("submission_id", self.ddata)
        self.assertIn("DATA", self.ddata)
        self.assertEqual(len(self.ddata["DATA"]), 0)

        # init with params
        self.assertEqual(self.param_ddata["label"], self.label)
        self.assertEqual(self.param_ddata["recursive"], "True")
        for par in self.params:
            self.assertEqual(self.param_ddata[par], self.params[par])

    def test_delete_add_item(self):
        """
        Adds an item to DeleteData, verifies results
        """
        # add item
        path = "source/path/"
        self.ddata.add_item(path)
        # verify results
        self.assertEqual(len(self.ddata["DATA"]), 1)
        data = self.ddata["DATA"][0]
        self.assertEqual(data["DATA_TYPE"], "delete_item")
        self.assertEqual(data["path"], path)
