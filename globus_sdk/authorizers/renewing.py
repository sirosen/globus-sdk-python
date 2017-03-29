import abc
import six
import logging
import time

from globus_sdk.authorizers.base import GlobusAuthorizer


logger = logging.getLogger(__name__)
# Provides a buffer for token expiration time to account for
# possible delays or clock skew.
EXPIRES_ADJUST_SECONDS = 60


@six.add_metaclass(abc.ABCMeta)
class RenewingAuthorizer(GlobusAuthorizer):
    """
    A ``RenwingAuthorizer`` is an abstract superclass to any authorizer
    that needs to get new Access Tokens in order to form Authorization headers.

    It may be passed an initial Access Token, but if so must also be passed
    an expires_at value for that token.

    It provides methods that handle the logic for checking and adjusting
    expiration time, callbacks on renewal, and 401 handling.

    To make an authorizer that implements this class simply implement
    the _get_token_response method for that authorization type.
    """

    def __init__(self, access_token=None, expires_at=None, on_refresh=None):
        logger.info(("Setting up a RenewingAuthorizer. It will use an "
                     "auth type of Bearer and can handle 401s."))
        if access_token is not None and expires_at is None:
            logger.warn(
                ("Initializing a RenewingAuthorizer with an "
                 "access_token and no expires_at time means that this "
                 "access_token will be discarded. You should either pass "
                 "expires_at or not pass an access_token at all"))
            # coerce to None for simplicity / consistency
            access_token = None

        self.access_token = access_token
        self.expires_at = None
        self.on_refresh = on_refresh

        # check access_token too -- it's not clear what it would mean to set
        # expiration without an access token
        if expires_at is not None and self.access_token is not None:
            logger.info(("Got both expires_at and access_token. "
                         "Will start by using "
                         "RenewingAuthorizer.access_token = ...{} "
                         "(last 5 chars)")
                        .format(self.access_token[-5:]))
            self._set_expiration_time(expires_at)

        # if these were unspecified, fetch a new access token
        if self.access_token is None and self.expires_at is None:
            logger.info("Creating RenewingAuthorizer without Access "
                        "Token. Fetching initial token now.")
            self._get_new_access_token()

    @abc.abstractmethod
    def _get_token_response(self):
        """
        Get a token_response using whatever flow or credentials
        the specific authorizer implementing this class uses.
        This response is expected to have an access_token field
        and a expires_at_seonds field at the top level.
        """

    def _set_expiration_time(self, expires_at):
        """
        Set the expiration time adjusting for potential network delays.
        """
        self.expires_at = expires_at - EXPIRES_ADJUST_SECONDS
        logger.debug(("Adjusted expiration time down to {} to account for "
                      "potential delays.")
                     .format(self.expires_at))

    def _get_new_access_token(self):
        """
        Given a token response from _get_token_response,
        set the access token and expiration time, and call on_refresh
        """
        token_response = self._get_token_response()
        self._set_expiration_time(token_response.expires_at_seconds)
        self.access_token = token_response.access_token
        logger.info(("RenewingAuthorizer.access_token updated to "
                     '"...{}" (last 5 chars)')
                    .format(self.access_token[-5:]))

        if callable(self.on_refresh):
            self.on_refresh(token_response)
            logger.debug("Invoked on_refresh callback")

    def _check_expiration_time(self):
        """
        Check if the expiration timer is done, and trigger a refresh if it is.
        """
        logger.debug("RenewingAuthorizer checking expiration time")
        if self.access_token is None or (
                self.expires_at is None or time.time() > self.expires_at):
            logger.debug(("RenewingAuthorizer determined time has "
                          "expired. Fetching new Access Token"))
            self._get_new_access_token()
        else:
            logger.debug(("RenewingAuthorizer determined time has "
                          "not yet expired"))

    def set_authorization_header(self, header_dict):
        """
        Checks to see if a new access token is needed.
        Once that's done, sets the ``Authorization`` header to
        "Bearer <access_token>"
        """
        self._check_expiration_time()
        logger.debug(("Setting RefreshToken Authorization Header:"
                      '"Bearer ...{}" (last 5 chars)')
                     .format(self.access_token[-5:]))
        header_dict['Authorization'] = "Bearer %s" % self.access_token

    def handle_missing_authorization(self, *args, **kwargs):
        """
        The refresh token handler can respond to a service 401 by immediately
        invalidating its current Access Token. When this happens, the next call
        to ``set_authorization_header()`` will result in a new Access Token
        being fetched.
        """
        logger.debug(("RenewingAuthorizer seeing 401. Invalidating "
                      "token and preparing for refresh."))
        # None for expires_at invalidates any current token
        self.expires_at = None
        # respond True, as in "we took some action, the 401 *may* be resolved"
        return True
