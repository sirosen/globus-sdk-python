try:
    import mock
except ImportError:
    from unittest import mock

from globus_sdk.authorizers import RefreshTokenAuthorizer
from tests.framework import CapturedIOTestCase


class RefreshTokenAuthorizerTests(CapturedIOTestCase):

    def setUp(self):
        """
        Sets up a RefreshTokenAuthorizer using a mock AuthClient for testing
        """
        super(RefreshTokenAuthorizerTests, self).setUp()
        # known values for testing
        self.refresh_token = "refresh_token_1"
        self.access_token = "access_token_1"
        self.expires_at = -1

        # mock response value for simulating a refresh token grant response
        self.mock_response = mock.Mock()
        self.mock_response.expires_at_seconds = -1
        self.mock_response.access_token = "access_token_2"

        # mock AuthClient for testing
        self.ac = mock.Mock()
        self.ac.oauth2_refresh_token = mock.Mock(
            return_value=self.mock_response)

        self.authorizer = RefreshTokenAuthorizer(
            self.refresh_token, self.ac, access_token=self.access_token,
            expires_at=self.expires_at)

    def test_get_token_response(self):
        """
        Calls _get_token_response, confirms that the mock AuthClient is used
        and the mock response was returned.
        """
        # get new_access_token
        res = self.authorizer._get_token_response()
        # confirm expected response
        self.assertEqual(res, self.mock_response)
        # confirm mock AuthClient was used as expected
        self.ac.oauth2_refresh_token.assert_called_once_with(
            self.refresh_token)
