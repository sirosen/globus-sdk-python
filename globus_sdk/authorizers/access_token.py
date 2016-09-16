from globus_sdk.authorizers.base import GlobusAuthorizer


class AccessTokenAuthorizer(GlobusAuthorizer):
    """
    Implements Authorization using a single Access Token with no Refresh
    Tokens. This is sent as a Bearer token in the header -- basically
    unadorned.

    **Parameters**

        ``access_token`` (*string*)
          An access token for Globus Auth
    """
    def __init__(self, access_token):
        self.access_token = access_token
        self.header_val = "Bearer %s" % access_token

    def set_authorization_header(self, header_dict):
        """
        Sets the ``Authorization`` header to
        "Bearer <access_token>"
        """
        header_dict['Authorization'] = self.header_val
