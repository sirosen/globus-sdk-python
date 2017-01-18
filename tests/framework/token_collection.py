import logging

import os
import unittest

log = logging.getLogger(__name__)


class TokenCollection(object):
    """
    A class which loads tokens from the environment, accessed via getters, and
    stores them in class attributes.

    Also provides a set of helpful skipunless decorators that wrap
    unittest.skip{Unless,If}

    Uses the class to act as a singleton
    """
    sdktester1a_native1_rt = os.environ.get(
        "SDKTESTER1A_NATIVEAPPCLIENT1_TRANSFER_RT")

    @classmethod
    def skip_unless_1a_native1_rt(cls):
        return unittest.skipIf(cls.sdktester1a_native1_rt is None,
                               ("No Token for sdktester1a@globusid.org on "
                                "Native App 1 found in environment"))
