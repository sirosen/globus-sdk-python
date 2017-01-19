import globus_sdk

from tests.framework import (
    CapturedIOTestCase, get_client_data,
    GO_EP1_ID, GO_EP2_ID, SDKTESTER1A_NATIVE1_RT)


class TransferClientTests(CapturedIOTestCase):
    def test_get_endpoint(self):
        """
        Get endpoint on go#ep1 and go#ep2, validate results
        """
        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_RT, ac)
        tc = globus_sdk.TransferClient(authorizer=authorizer)

        # load the tutorial endpoint documents
        ep1_doc = tc.get_endpoint(GO_EP1_ID)
        ep2_doc = tc.get_endpoint(GO_EP2_ID)

        # check that their contents are at least basically sane (i.e. we didn't
        # get empty dicts or something)
        self.assertIn("display_name", ep1_doc)
        self.assertIn("display_name", ep2_doc)
        self.assertIn("canonical_name", ep1_doc)
        self.assertIn("canonical_name", ep2_doc)

        # double check the canonical name fields, consider this done
        self.assertEqual(ep1_doc["canonical_name"], "go#ep1")
        self.assertEqual(ep2_doc["canonical_name"], "go#ep2")
