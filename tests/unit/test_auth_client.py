import globus_sdk
from tests.framework import (CapturedIOTestCase,
                             get_client_data, get_user_data,
                             SDKTESTER1A_NATIVE1_AUTH_RT)
from globus_sdk.auth import (GlobusNativeAppFlowManager,
                             GlobusAuthorizationCodeFlowManager)
from globus_sdk.exc import GlobusAPIError


class AuthClientTests(CapturedIOTestCase):

    def setUp(self):
        """
        Instantiates an AuthClient with an access_token authorizer
        """
        super(AuthClientTests, self).setUp()

        self.access_token = self.test_oauth2_token()
        self.ac = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(self.access_token),
            client_id=get_client_data()["native_app_client1"]["id"])

    def test_get_identities(self):
        """
        Makes calls to the get identities resource using singleton and lists
        of ids and usernames, both in use and not. Validates results.
        Confirms incorrect requests throw GlobusAPIErrors
        """
        def get_identity(identities, uid=None, username=None):
            """
            helper for getting identities since response order isn't guaranteed
            """
            for identity in identities:
                if identity["id"] == uid or identity["username"] == username:
                    return identity
            return None

        # expected values
        sdk_expected = get_user_data()["sdktester1a"]
        go_expected = get_user_data()["go"]

        # get single ID
        id_res = self.ac.get_identities(
            ids=get_user_data()["sdktester1a"]["id"])
        sdk_identity = get_identity(
            id_res["identities"], uid=get_user_data()["sdktester1a"]["id"])
        for item in sdk_expected:
            self.assertEqual(sdk_identity[item], sdk_expected[item])

        # get multiple IDs
        unused_id = "12345678-1234-1234-1234-1234567890ab"
        ids = [get_user_data()["sdktester1a"]["id"],
               get_user_data()["go"]["id"], unused_id]
        id_res = self.ac.get_identities(ids=ids)
        # validate sdk
        sdk_identity = get_identity(
            id_res["identities"], uid=get_user_data()["sdktester1a"]["id"])
        for item in sdk_expected:
            self.assertEqual(sdk_identity[item], sdk_expected[item])
        # validate go
        go_identity = get_identity(id_res["identities"],
                                   uid=get_user_data()["go"]["id"])
        for item in go_expected:
            self.assertEqual(go_identity[item], go_expected[item])
        unused_identity = get_identity(id_res["identities"], uid=unused_id)
        # confirm unused id isn't returned
        self.assertIsNone(unused_identity)

        # get single username
        id_res = self.ac.get_identities(
            usernames=get_user_data()["sdktester1a"]["username"])
        sdk_identity = get_identity(
            id_res["identities"],
            username=get_user_data()["sdktester1a"]["username"])
        for item in sdk_expected:
            self.assertEqual(sdk_identity[item], sdk_expected[item])

        # get multiple usernames
        unused_username = "unused@unused.org"
        usernames = [get_user_data()["sdktester1a"]["username"],
                     get_user_data()["go"]["username"], unused_username]
        id_res = self.ac.get_identities(usernames=usernames)
        # validate sdk
        sdk_identity = get_identity(
            id_res["identities"],
            username=get_user_data()["sdktester1a"]["username"])
        for item in sdk_expected:
            self.assertEqual(sdk_identity[item], sdk_expected[item])
        # validate go
        go_identity = get_identity(
            id_res["identities"], username=get_user_data()["go"]["username"])
        for item in go_expected:
            self.assertEqual(go_identity[item], go_expected[item])
        unused_identity = get_identity(id_res["identities"],
                                       username=unused_username)
        # validate unused
        self.assertEqual(unused_identity["username"], unused_username)
        self.assertEqual(unused_identity["name"], None)
        self.assertEqual(unused_identity["status"], "unused")

        # bad request
        with self.assertRaises(GlobusAPIError) as apiErr:
            self.ac.get_identities(usernames=usernames, ids=ids)
        self.assertEqual(apiErr.exception.http_status, 400)
        self.assertEqual(apiErr.exception.code, "INVALID_PARAMETERS")

        # no auth
        with self.assertRaises(GlobusAPIError) as apiErr:
            globus_sdk.AuthClient().get_identities()
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "UNAUTHORIZED")

    def test_oauth2_get_authorize_url(self):
        """
        Gets an authorize url after starting a native app auth flow, a
        confidential app auth flow, and no auth flow. Validates results.
        """
        base_url = "https://auth.globus.org/v2/"

        # no auth flow
        with self.assertRaises(ValueError):
            self.ac.oauth2_get_authorize_url()

        # native auth flow
        self.ac.current_oauth2_flow_manager = GlobusNativeAppFlowManager(
            self.ac, None)
        url_res = self.ac.oauth2_get_authorize_url()
        # validate results
        expected_vals = [base_url + "oauth2/authorize?", "code_challenge=",
                         "scope=", "openid", "profile", "email",
                         "access_type=online", "state=_default",
                         "response_type=code",
                         "client_id=" + self.ac.client_id]
        for val in expected_vals:
            self.assertIn(val, url_res)

        # confidential auth flow
        uri = "test-redirect-uri.org"
        self.ac.current_oauth2_flow_manager = (
            GlobusAuthorizationCodeFlowManager(self.ac, uri))
        url_res = self.ac.oauth2_get_authorize_url()
        # validate results
        expected_vals = [base_url + "oauth2/authorize?",
                         "access_type=online", "state=_default",
                         "scope=", "openid", "profile", "email",
                         "response_type=code", "redirect_uri=" + uri,
                         "client_id=" + self.ac.client_id]
        for val in expected_vals:
            self.assertIn(val, url_res)

    def test_oauth2_exchange_code_for_tokens(self):
        """
        Confirms flow required and an invalid code returns a 401,
        Correct usage can only be tested in integration tests
        """
        # no auth flow
        with self.assertRaises(ValueError):
            self.ac.oauth2_exchange_code_for_tokens("")

        # bad code
        self.ac.current_oauth2_flow_manager = GlobusNativeAppFlowManager(
            self.ac, None)
        with self.assertRaises(GlobusAPIError) as apiErr:
            self.ac.oauth2_exchange_code_for_tokens("bad_code")
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "Error")  # json is malformed?

    def test_oauth2_refresh_token(self):
        """
        Gets an access token from the testing Refresh Token, validates results
        """
        param = {"client_id": self.ac.client_id}
        ref_res = self.ac.oauth2_refresh_token(
            SDKTESTER1A_NATIVE1_AUTH_RT, additional_params=param)
        self.assertIn("access_token", ref_res)
        self.assertIn("expires_in", ref_res)
        self.assertIn("scope", ref_res)
        self.assertEqual(ref_res["resource_server"], "auth.globus.org")
        self.assertEqual(ref_res["token_type"], "Bearer")

        # without valid client id
        with self.assertRaises(GlobusAPIError) as apiErr:
            ref_res = self.ac.oauth2_refresh_token(SDKTESTER1A_NATIVE1_AUTH_RT)
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "Error")  # json is malformed?

    def test_oauth2_revoke_token(self):
        """
        Revokes the access_token used in test AuthClient's authorizer
        Confirms can no longer make authorized requests
        """
        param = {"client_id": self.ac.client_id}
        rev_res = self.ac.oauth2_revoke_token(self.access_token,
                                              additional_params=param)
        self.assertFalse(rev_res["active"])

        with self.assertRaises(GlobusAPIError) as apiErr:
            self.ac.get_identities()
        self.assertEqual(apiErr.exception.http_status, 401)
        self.assertEqual(apiErr.exception.code, "UNAUTHORIZED")

    def test_oauth2_token(self):
        """
        Gets an access_token using oauth2/token directly, validates results
        returns the access_token for use in testing
        """
        client_id = get_client_data()["native_app_client1"]["id"]
        form_data = {'refresh_token': SDKTESTER1A_NATIVE1_AUTH_RT,
                     'grant_type': 'refresh_token',
                     'client_id': client_id}
        # valid client
        token_res = globus_sdk.AuthClient().oauth2_token(form_data)
        self.assertIn("access_token", token_res)
        self.assertIn("expires_in", token_res)
        self.assertIn("scope", token_res)

        return token_res["access_token"]

    def test_oauth2_userinfo(self):
        """
        Gets userinfo, validates results
        Confirms unauthorized client cannot access userinfo
        """
        userinfo_res = self.ac.oauth2_userinfo()
        self.assertEqual(
            userinfo_res["preferred_username"],
            get_user_data()["sdktester1a"]["username"])
        self.assertEqual(
            userinfo_res["name"],
            get_user_data()["sdktester1a"]["name"])
        self.assertEqual(
            userinfo_res["sub"],
            get_user_data()["sdktester1a"]["id"])

        # unauthorized client
        with self.assertRaises(GlobusAPIError) as apiErr:
            globus_sdk.AuthClient().oauth2_userinfo()
        self.assertEqual(apiErr.exception.http_status, 403)
        self.assertEqual(apiErr.exception.code, "FORBIDDEN")
