"""
Test that our DeprecationWarnings and PendingDeprecationWarnings are being
displayed correctly on stderr, and under the right conditions.
"""

import sys
import warnings

from globus_sdk.nexus import NexusClient

from globus_sdk.tests.framework import CapturedIOTestCase


class DeprecationWarningsTests(CapturedIOTestCase):
    def setUp(self):
        CapturedIOTestCase.setUp(self)
        warnings.resetwarnings()
        self._clear_warnings_registry()

    def _clear_warnings_registry(self):
        """
        Clear the warnings registry on every module because resetwarnings()
        doesn't do this for us.
        """
        # that's right, walk over *all* modules and clear it *everywhere*
        # we can limit this to globus_sdk in the future, but it seems like
        # unnecessary work
        for _, mod in sys.modules.items():
            registry = getattr(mod, "__warningregistry__", None)
            if registry:
                registry.clear()

    def test_nexus_client_instantiation_warning_enabled(self):
        """
        Nexus Client Prints Deprecation Warning
        """
        warnings.simplefilter('always')
        NexusClient()

        expected = NexusClient._DEPRECATION_TEXT
        err = self.stderr.getvalue()
        assert expected in err, '{} not in {}'.format(expected, err)

    def test_nexus_client_instantiation_warning_disabled(self):
        """
        Nexus Client Deprecation Warning Suppressed by Ignore Rule
        """
        warnings.simplefilter('ignore', PendingDeprecationWarning)
        warnings.simplefilter('ignore', DeprecationWarning)
        NexusClient()

        not_expected = NexusClient._DEPRECATION_TEXT
        err = self.stderr.getvalue()
        assert not_expected not in err, (
            '{} unexpectedly found in {}'.format(not_expected, err))

    def test_nexus_client_instantiation_warning_exactly_once(self):
        """
        Nexus Client Deprecation Warning -- Warn Once Behavior
        """
        warnings.simplefilter('once', PendingDeprecationWarning)
        warnings.simplefilter('once', DeprecationWarning)
        NexusClient()
        NexusClient()

        expected = NexusClient._DEPRECATION_TEXT
        err = self.stderr.getvalue()
        assert expected in err, (
            '{} not in {}'.format(expected, err))
        assert err.count(expected) == 1, (
            '{} occurs more than once in {}'.format(expected, err))
