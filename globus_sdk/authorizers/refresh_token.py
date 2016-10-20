import logging
import time

from globus_sdk.authorizers.base import GlobusAuthorizer

logger = logging.getLogger(__name__)


# Provides a buffer for token expiration time to account for
# possible delays or clock skew.
EXPIRES_ADJUST_SECONDS = 60


class RefreshTokenAuthorizer(GlobusAuthorizer):
    """
    Implements Authorization using a Refresh Token to periodically fetch
    renewed Access Tokens. It may be initialized with an Access Token, or it
    will fetch one the first time that ``set_authorization_header()`` is
    called.

    This Authorizer is by far the most sophisticated ``GlobusAuthorizer``.
    Example usage looks something like this:

    >>> import globus_sdk
    >>> auth_client = globus_sdk.AuthClient(client_id=..., client_secret=...)
    >>> # do some flow to get a refresh token from auth_client
    >>> rt_authorizer = globus_sdk.RefreshTokenAuthorizer(
    >>>     refresh_token, auth_client)
    >>> # create a new client
    >>> transfer_client = globus_sdk.TransferClient(authorizer=rt_authorizer)

    anything that inherits from :class:`BaseClient <globus_sdk.BaseClient>`, so
    at least ``TransferClient`` and ``AuthClient`` will automatically handle
    usage of the ``RefreshTokenAuthorizer``.

    **Parameters**

        ``refresh_token`` (*string*)
          Refresh Token for Globus Auth

        ``auth_client`` (:class:`AuthClient <globus_sdk.AuthClient>`)
          ``AuthClient`` capable of using the ``refresh_token``

        ``access_token`` (*string*)
          Initial Access Token to use, only used if ``expires_at`` is also set

        ``expires_at`` (*int*)
          Expiration time for the starting ``access_token`` expressed as a
          POSIX timestamp (i.e. seconds since the epoch)

        ``on_refresh`` (*callable*)
        Will be called as fn(TokenResponse) any time this authorizer
        fetches a new access_token
    """
    def __init__(self, refresh_token, auth_client,
                 access_token=None, expires_at=None, on_refresh=None):
        logger.info(("Setting up a RefreshTokenAuthorizer. It will use an "
                     "auth type of Bearer and can handle 401s."))
        logger.info("RefreshTokenAuthorizer.auth_client = instance:{}"
                    .format(id(auth_client)))
        if access_token is not None and expires_at is None:
            logger.warn(
                ("Initializing a RefreshTokenAuthorizer with an "
                 "access_token and no expires_at time means that this "
                 "access_token will be discarded. You should either pass "
                 "expires_at or not pass an access_token at all"))
            # coerce to None for simplicity / consistency
            access_token = None

        # required
        self.refresh_token = refresh_token
        self.auth_client = auth_client

        # not required
        self.access_token = access_token
        self.expires_at = None
        self.on_refresh = on_refresh

        # check access_token too -- it's not clear what it would mean to set
        # expiration without an access token
        if expires_at is not None and self.access_token is not None:
            logger.info(("Got both expires_at and access_token. "
                         "Will start by using "
                         "RefreshTokenAuthorizer.access_token = ...{} "
                         "(last 5 chars)")
                        .format(self.access_token[-5:]))
            self._set_expiration_time(expires_at)

        # if these were unspecified, fetch a new access token
        if self.access_token is None and self.expires_at is None:
            logger.info("Creating RefreshTokenAuthorizer without Access "
                        "Token. Fetching initial token now.")
            self._get_new_access_token()

    def _set_expiration_time(self, expires_at):
        """
        Set the expiration time.
        """
        self.expires_at = expires_at - EXPIRES_ADJUST_SECONDS
        logger.debug(("Adjusted expiration time down to {} to account for "
                      "potential delays.")
                     .format(self.expires_at))

    def _get_new_access_token(self):
        """
        Get a new Access Token by asking the AuthClient that we have to do a
        token refresh.
        Records the new expiration time and the new access token. Ob-la-di,
        ob-la-da.
        """
        token_response = self.auth_client.oauth2_refresh_token(
            self.refresh_token)
        self._set_expiration_time(token_response.expires_at_seconds)
        self.access_token = token_response.access_token
        logger.info(("RefreshTokenAuthorizer.access_token updated to "
                     '"...{}" (last 5 chars)')
                    .format(self.access_token[-5:]))

        if callable(self.on_refresh):
            self.on_refresh(token_response)
            logger.debug("Invoked on_refresh callback")

    def _check_expiration_time(self):
        """
        Check if the expiration timer is done, and trigger a refresh if it is.
        """
        logger.debug("RefreshTokenAuthorizer checking expiration time")
        if self.access_token is None or (
                self.expires_at is None or time.time() > self.expires_at):
            logger.debug(("RefreshTokenAuthorizer determined time has "
                          "expired. Fetching new Access Token"))
            self._get_new_access_token()
        else:
            logger.debug(("RefreshTokenAuthorizer determined time has "
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
        logger.debug(("RefreshTokenAuthorizer seeing 401. Invalidating "
                      "token and preparing for refresh."))
        # None for expires_at invalidates any current token
        self.expires_at = None
        # respond True, as in "we took some action, the 401 *may* be resolved"
        return True
