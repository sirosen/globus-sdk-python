# -*- coding: utf-8 -*-
import base64
import six

from nose2.tools.params import params

from globus_sdk.authorizers import BasicAuthorizer
from tests.framework import CapturedIOTestCase


class BasicAuthorizerTests(CapturedIOTestCase):

    def setUp(self):
        """
        Initializes a BasicAuthorizer for testing
        """
        super(BasicAuthorizerTests, self).setUp()
        self.username = "testUser"
        self.password = "PASSWORD"
        self.authorizer = BasicAuthorizer(self.username, self.password)

    def test_set_authorization_header(self):
        """
        Sets authorization header in a test dictionary, confirms expected value
        """
        header_dict = {}
        self.authorizer.set_authorization_header(header_dict)
        # confirm value
        self.assertEqual(header_dict["Authorization"][:6], "Basic ")
        decoded = base64.b64decode(
            six.b(header_dict["Authorization"][6:])).decode('utf-8')
        self.assertEqual(decoded, "{0}:{1}".format(self.username,
                                                   self.password))

    def test_set_authorization_header_existing(self):
        """
        Confirms that an existing Authorization field is overwritten
        """
        header_dict = {"Header": "value",
                       "Authorization": "previous_value"}
        self.authorizer.set_authorization_header(header_dict)
        # confirm values
        self.assertEqual(header_dict["Authorization"][:6], "Basic ")
        decoded = base64.b64decode(
            six.b(header_dict["Authorization"][6:])).decode('utf-8')
        self.assertEqual(decoded, "{0}:{1}".format(self.username,
                                                   self.password))
        self.assertEqual(header_dict["Header"], "value")

    def test_handle_missing_authorization(self):
        """
        Confirms that BasicAuthorizer doesn't handle missing authorization
        """
        self.assertFalse(self.authorizer.handle_missing_authorization())

    @params(("user", u"テスト"), (u"дум", 'pass'), (u"テスト", u"дум"))
    def test_unicode_handling(self, username, password):
        """
        With a unicode string for the password, set and verify the
        Authorization header.
        """
        header_dict = {}
        authorizer = BasicAuthorizer(username, password)
        authorizer.set_authorization_header(header_dict)
        # confirm value
        self.assertEqual(header_dict["Authorization"][:6], "Basic ")
        decoded = base64.b64decode(
            six.b(header_dict["Authorization"][6:])).decode('utf-8')
        self.assertEqual(decoded,
                         u"{0}:{1}".format(username, password))
