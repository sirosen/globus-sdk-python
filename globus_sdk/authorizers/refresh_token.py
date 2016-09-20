import warnings
import time
from globus_sdk.authorizers.base import GlobusAuthorizer

# a percent error expected in the `expires_in` values on AccessTokens,
# expressed as a fractional value
# taken out of the expiration value, not the total time (because that would be
# weird, yeah?)
# This is 5%, not 0.05%!
_EXPIRATION_PERCENT_ERROR = 0.05
# this is a fixed number of seconds to be pulled down from the expiration
# timer, so that when the expires_in value is very small, the percent error
# doesn't go to 0 and make us run the timer all the way down
# so, we want (NOW - expires_in - (expires_in*PCT_ERROR) - FIXED_ERROR)
# ultimately
_EXPIRATION_FIXED_ERROR = 5


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
          Initial Access Token to use, only used if ``expires_in`` is also set

        ``expires_in`` (*int*)
          Expiration time for the starting ``access_token`` expressed as
          seconds in the future
    """
    def __init__(self, refresh_token, auth_client,
                 access_token=None, expires_in=None):
        if access_token is not None and expires_in is None:
            warnings.warn(
                ("Initializing a RefreshTokenAuthorizer with an "
                 "access_token and no expires_in time means that this "
                 "access_token will be discarded. You should either pass "
                 "expires_in or not pass an access_token at all"))
            # coerce to None for simplicity / consistency
            access_token = None

        # required
        self.refresh_token = refresh_token
        self.auth_client = auth_client

        # not required
        self.access_token = access_token
        self.expires_at = None

        # check access_token too -- it's not clear what it would mean to set
        # expiration without an access token
        if expires_in is not None and self.access_token is not None:
            self._set_expiration_time(expires_in)

        # if these were unspecified, fetch a new access token
        if self.access_token is None and self.expires_at is None:
            self._get_new_access_token()

    def _set_expiration_time(self, expires_in):
        """
        Set the expiration time, accounting for the fixed and percent error
        expected in expiration timers. This error accounts for any jitter that
        may be introduced by network delays &c., async clocks between the
        client and server, and unknown quirky delays between the response being
        received and processed.
        """
        # happens to be a floating point value -- that's fine, no need to int()
        # it, since we'll never do == comparisons anyway
        self.expires_at = time.time() + expires_in - (
            _EXPIRATION_PERCENT_ERROR * expires_in) - _EXPIRATION_FIXED_ERROR

    def _get_new_access_token(self):
        """
        Get a new Access Token by asking the AuthClient that we have to do a
        token refresh.
        Records the new expiration time and the new access token. Ob-la-di,
        ob-la-da.
        """
        token_response = self.auth_client.oauth2_refresh_token(
            self.refresh_token)
        self._set_expiration_time(token_response.expires_in)
        self.access_token = token_response.access_token

    def _check_expiration_time(self):
        """
        Check if the expiration timer is done, and trigger a refresh if it is.
        """
        if self.access_token is None or (
                self.expires_at is None or time.time() > self.expires_at):
            self._get_new_access_token()

    def set_authorization_header(self, header_dict):
        """
        Checks to see if a new access token is needed.
        Once that's done, sets the ``Authorization`` header to
        "Bearer <access_token>"
        """
        self._check_expiration_time()
        header_dict['Authorization'] = "Bearer %s" % self.access_token

    def handle_missing_authorization(self, *args, **kwargs):
        """
        The refresh token handler can respond to a service 401 by immediately
        invalidating its current Access Token. When this happens, the next call
        to ``set_authorization_header()`` will result in a new Access Token
        being fetched.
        """
        # None for expires_at invalidates any current token
        self.expires_at = None
        # respond True, as in "we took some action, the 401 *may* be resolved"
        return True
