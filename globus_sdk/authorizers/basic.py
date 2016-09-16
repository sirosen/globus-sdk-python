import base64

from globus_sdk.authorizers.base import GlobusAuthorizer


class BasicAuthorizer(GlobusAuthorizer):
    """
    This Authorizer implements Basic Authentication.
    Given a "username" and "password", they are sent base64 encoded in the
    header.

    **Parameters**

        ``username`` (*string*)
          Username component for Basic Auth

        ``password`` (*string*)
          Password component for Basic Auth
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        encoded = base64.b64encode("%s:%s" % (username, password))
        self.header_val = "Basic %s" % encoded

    def set_authorization_header(self, header_dict):
        """
        Sets the ``Authorization`` header to
        "Basic <base64 encoded username:password>"
        """
        header_dict['Authorization'] = self.header_val
