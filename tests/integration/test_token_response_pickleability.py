import logging
import os
import pickle
import tempfile

import globus_sdk
from tests.framework import (CapturedIOTestCase,
                             get_client_data, GO_EP1_ID,
                             SDKTESTER1A_NATIVE1_TRANSFER_RT,
                             retry_errors)


class RefreshTokenResponsePickleTests(CapturedIOTestCase):

    def setUp(self):
        """
        Do a refresh_token grant token call to get token responses, test with
        those results that.
        """
        super(RefreshTokenResponsePickleTests, self).setUp()

        client_id = get_client_data()["native_app_client1"]["id"]
        form_data = {'refresh_token': SDKTESTER1A_NATIVE1_TRANSFER_RT,
                     'grant_type': 'refresh_token',
                     'client_id': client_id}
        self.ac = globus_sdk.AuthClient()
        # add a logger with an open file handle to ensure that the client
        # cannot be pickled -- this is the common way that pickleability is
        # broken
        # also, this looks odd -- logger.logger -- but it's correct, "logger"
        # is what we named our LoggerAdapter, and "logger" is the name of the
        # underlying logger object on a LoggerAdapter
        tmplog_handle, self.tmplog = tempfile.mkstemp()
        self.ac.logger.logger.addHandler(logging.FileHandler(self.tmplog))
        self.token_response = self.ac.oauth2_token(form_data)

    def tearDown(self):
        """
        Clean up the temp log file
        """
        try:
            os.remove(self.tmplog)
        except OSError:
            pass

    def mint_new_transfer_client(self, response=None):
        response = response or self.token_response

        access_token = response.by_resource_server[
            'transfer.api.globus.org']['access_token']

        authorizer = globus_sdk.AccessTokenAuthorizer(access_token)
        return globus_sdk.TransferClient(authorizer=authorizer)

    def test_pickle_and_unpickle_no_usage(self):
        """
        Test pickle and unpickle, with no usage of the result,
        for all pickle protocol versions supported by the current interpreter.
        """
        pickled_versions = [pickle.dumps(self.token_response, protocol=n)
                            for n in range(pickle.HIGHEST_PROTOCOL + 1)]
        unpickled_versions = [pickle.loads(x) for x in pickled_versions]
        for x in unpickled_versions:
            self.assertDictEqual(x.by_resource_server,
                                 self.token_response.by_resource_server)

    @retry_errors()
    def test_pickle_unpickle_and_ls(self):
        """
        Pickle a response, unpickle it, use it to build an authorizer and do an
        `ls`, verify against the "straight" version which builds the authorizer
        without a pickle/unpickle pass
        """
        sour_tc = self.mint_new_transfer_client(
            response=pickle.loads(pickle.dumps(self.token_response)))

        # confirm the resulting client still works!
        get_res = sour_tc.get_endpoint(GO_EP1_ID)
        self.assertEqual(get_res["id"], GO_EP1_ID)
