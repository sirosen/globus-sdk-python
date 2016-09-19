"""
Test Config Loading produces expected results.
"""

import os
import unittest

try:
    import mock
except ImportError:
    from unittest import mock

import globus_sdk.config


class ConfigLoaderTests(unittest.TestCase):
    def _load_config_file(self, filename):
        filename = os.path.join(
            os.path.dirname(__file__),
            'sample_configs',
            filename)

        globus_sdk.config._parser = None

        def loadconf(cfgparser):
            cfgparser._read([filename])

        with mock.patch(
                'globus_sdk.config.GlobusConfigParser._load_config', loadconf):
            globus_sdk.config._get_parser()

    def test_default_auth_tkn(self):
        self._load_config_file('default_auth_tkn.cfg')
        assert globus_sdk.config.get_auth_token('default') == 'abc123'
        assert globus_sdk.config.get_auth_token('general') == 'abc123'
        assert globus_sdk.config.get_auth_token(
            'definitelynonexistintsection') == 'abc123'

    def test_per_env_auth_tkn(self):
        self._load_config_file('per_env_auth_tkn.cfg')

        assert globus_sdk.config.get_auth_token('general') == 'abc123'
        assert globus_sdk.config.get_auth_token('default') == 'XYZ0'
        assert globus_sdk.config.get_auth_token('beta') == 'XYZ1'

    def test_verify_ssl_true(self):
        self._load_config_file('verify_ssl_true.cfg')

        assert globus_sdk.config.get_ssl_verify('default') is True

    def test_verify_ssl_false(self):
        self._load_config_file('verify_ssl_false.cfg')

        assert globus_sdk.config.get_ssl_verify('default') is False

    def test_verify_ssl_invalid(self):
        self._load_config_file('verify_ssl_invalid.cfg')

        with self.assertRaises(ValueError):
            globus_sdk.config.get_ssl_verify('default')
