from globus_sdk.authorizers.base import GlobusAuthorizer


class NullAuthorizer(GlobusAuthorizer):
    """
    This Authorizer implements No Authentication -- as in, it ensures that
    there is no Authorization header.
    """
    def set_authorization_header(self, header_dict):
        """
        Removes the Authorization header from the given header dict if one was
        present.
        """
        header_dict.pop('Authorization', None)
