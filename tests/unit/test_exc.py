import requests
import json
import six

from globus_sdk.exc import (GlobusAPIError, TransferAPIError,
                            GlobusOptionalDependencyError)
from tests.framework import CapturedIOTestCase


# super class for Globus and Transfer APIError tests with shared setup
class APIErrorTests(CapturedIOTestCase):

    __test__ = False  # prevents base class from trying to run tests

    def setUp(self):
        """
        Creates a json error response a text error response, and a malformed
        json response for testing
        """
        super(APIErrorTests, self).setUp()

        self.json_data = {"errors": [{"message": "json error message",
                                      "code": "Json Error"}]}
        self.json_response = requests.Response()
        self.json_response._content = six.b(json.dumps(self.json_data))
        self.json_response.headers["Content-Type"] = "application/json"
        self.json_response.status_code = "400"

        self.text_data = "error message"
        self.text_response = requests.Response()
        self.text_response._content = six.b(self.text_data)
        self.text_response.headers["Content-Type"] = "text/plain"
        self.text_response.status_code = "401"

        self.malformed_response = requests.Response()
        self.malformed_response._content = six.b("{")
        self.malformed_response.headers["Content-Type"] = "application/json"
        self.malformed_response.status_code = "403"


class GlobusAPIErrorTests(APIErrorTests):

    __test__ = True  # marks sub-class as having tests

    def test_raw_json(self):
        """
        Confirms the GlobusAPIError can get raw json from the json responses,
        and defaults to text for the text response
        """
        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        self.assertEqual(apiErr.exception.raw_json, self.json_data)

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        self.assertEqual(apiErr.exception.raw_json, None)

        # malformed
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.malformed_response)
        self.assertEqual(apiErr.exception.raw_json, None)

    def test_raw_text(self):
        """
        Gets raw text from both json and text responses, confirms results
        """
        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        self.assertEqual(apiErr.exception.raw_text, json.dumps(self.json_data))

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        self.assertEqual(apiErr.exception.raw_text, self.text_data)

    def test_get_args(self):
        """
        Gets args from json text and malformed responses, confirms results
        Implicitly tests _load_from_json and _load_from_text
        """

        # json
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.json_response)
        expected = ("400", "Json Error", "json error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # text
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.text_response)
        expected = ("401", "Error", "error message")
        self.assertEqual(apiErr.exception._get_args(), expected)

        # malformed
        with self.assertRaises(GlobusAPIError) as apiErr:
            raise GlobusAPIError(self.malformed_response)
        expected = ("403", "Error", "{")
        self.assertEqual(apiErr.exception._get_args(), expected)


class TransferAPIErrorTests(APIErrorTests):

    __test__ = True  # marks sub-class as having tests

    def setUp(self):
        """
        Creates a transfer-like json response in addition to the APIError
        setUp responses for testing
        """
        super(TransferAPIErrorTests, self).setUp()

        self.transfer_data = {"message": "transfer error message",
                              "code": "Transfer Error", "request_id": 123}
        self.transfer_response = requests.Response()
        self.transfer_response._content = six.b(json.dumps(self.transfer_data))
        self.transfer_response.headers["Content-Type"] = "application/json"
        self.transfer_response.status_code = "404"

    def test_get_args(self):
        """
        Gets args from all four response types, confirms expected results
        implicitly tests _load_from_json
        """
        # transfer
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.transfer_response)
        expected = ("404", "Transfer Error", "transfer error message", 123)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # json in wrong format
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.json_response)
        expected = ("400", "Error", json.dumps(self.json_data), None)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # text
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.text_response)
        expected = ("401", "Error", "error message", None)
        self.assertEqual(apiErr.exception._get_args(), expected)

        # malformed json
        with self.assertRaises(TransferAPIError) as apiErr:
            raise TransferAPIError(self.malformed_response)
        expected = ("403", "Error", "{", None)
        self.assertEqual(apiErr.exception._get_args(), expected)


class GlobusOptionalDependencyErrorTests(CapturedIOTestCase):

    def test_init(self):
        """
        Creates a GlobusOptionalDependencyError, confirms message is set
        """

        feature_name = "feature"
        dep_names = ["dep1", "dep2", "dep3"]
        with self.assertRaises(GlobusOptionalDependencyError) as depErr:
            raise GlobusOptionalDependencyError(dep_names, feature_name)
        self.assertIn("in order to use " + feature_name,
                      depErr.exception.message)
        for dep in dep_names:
            self.assertIn(dep + "\n", depErr.exception.message)
