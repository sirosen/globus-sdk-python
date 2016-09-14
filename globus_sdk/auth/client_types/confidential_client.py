from globus_sdk.authorizers import BasicAuthorizer
from globus_sdk.auth.oauth2_constants import DEFAULT_REQUESTED_SCOPES
from globus_sdk.auth.client_types.base import AuthClient


class ConfidentialAppAuthClient(AuthClient):
    """
    This is a specialized type of ``AuthClient`` used to represent an App with
    a Client ID and Client Secret wishing to communicate with Globus Auth.
    It must be given a Client ID and a Client Secret, and furthermore, these
    will be used to establish a :class:`BasicAuthorizer
    <globus_sdk.authorizers.BasicAuthorizer` for authorization purposes.
    Additionally, the Client ID is stored for use in various calls.

    Confidential Applications (i.e. Applications with are not Native Apps) are
    those like the `Sample Data Portal
    <https://github.com/globus/globus-sample-data-portal>`_, which have their
    own credentials for authenticating against Globus Auth.

    Any keyword arguments given are passed through to the ``AuthClient``
    constructor.
    """
    # checked by BaseClient to see what authorizers are allowed for this client
    # subclass
    # only allow basic auth -- anything else means you're misusing the client
    allowed_authorizer_types = [BasicAuthorizer]

    def __init__(self, client_id, client_secret, **kwargs):
        if "authorizer" in kwargs:
            raise ValueError(
                "Cannot give a ConfidentialAppAuthClient an authorizer")

        AuthClient.__init__(
            self, client_id=client_id,
            authorizer=BasicAuthorizer(client_id, client_secret),
            **kwargs)

    def oauth2_client_credentials_token(self, requested_scopes=None):
        """
        Perform an OAuth2 Client Credentials Grant to get access tokens which
        directly represent your client and allow it to act on its own
        (independent of any user authorization).
        This method does not use a ``GlobusOAuthFlowManager`` because it is not
        at all necessary to do so.

        ``requested_scopes``
          A string of space-separated scope names being requested for the
          access token(s). Defaults to a set of commonly desired scopes for
          Globus.

        :rtype: :class:`OAuthTokenResponse \
        <globus_sdk.auth.token_response.OAuthTokenResponse>`

        For example, with a Client ID of "CID1001" and a Client Secret of
        "RAND2002", you could use this grant type like so:

        >>> client = ConfidentialAppAuthClient("CID1001", "RAND2002")
        >>> tokens = client.oauth2_client_credentials_token()
        >>> transfer_token_info = tokens.by_resource_server["transfer.api.globus.org"]
        >>> transfer_token = transfer_token_info["access_token"]
        """
        requested_scopes = requested_scopes or DEFAULT_REQUESTED_SCOPES

        return self.oauth2_token({
            'grant_type': 'client_credentials',
            'scope': requested_scopes})
