# coding=utf-8
import unittest

from globus_sdk import utils


class TestUtils(unittest.TestCase):

    def test_safe_b64encode_non_ascii(self):
        test_string = 'ⓤⓢⓔⓡⓝⓐⓜⓔ'
        expected_b64 = '4pOk4pOi4pOU4pOh4pOd4pOQ4pOc4pOU'

        self.assertEqual(utils.safe_b64encode(test_string), expected_b64)

    def test_safe_b64encode_ascii(self):
        test_string = 'username'
        expected_b64 = 'dXNlcm5hbWU='

        self.assertEqual(utils.safe_b64encode(test_string), expected_b64)
