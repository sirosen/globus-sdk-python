import logging

from globus_sdk.authorizers.base import GlobusAuthorizer
from globus_sdk.utils import safe_b64encode

logger = logging.getLogger(__name__)


class BasicAuthorizer(GlobusAuthorizer):
    """
    This Authorizer implements Basic Authentication.
    Given a "username" and "password", they are sent base64 encoded in the
    header.

    :param username: Username component for Basic Auth
    :type username: str
    :param password: Password component for Basic Auth
    :type password: str
    """

    def __init__(self, username, password):
        logger.info(
            "Setting up a BasicAuthorizer. It will use an "
            "auth type of Basic and cannot handle 401s."
        )
        logger.info(f"BasicAuthorizer.username = {username}")
        self.username = username
        self.password = password

        to_b64 = f"{username}:{password}"
        self.header_val = "Basic %s" % safe_b64encode(to_b64)

    def set_authorization_header(self, header_dict):
        """
        Sets the ``Authorization`` header to
        "Basic <base64 encoded username:password>"
        """
        logger.debug(
            ("Setting Basic Authorization Header: " '"Basic <{}:SECRET>"').format(
                self.username
            )
        )
        header_dict["Authorization"] = self.header_val
