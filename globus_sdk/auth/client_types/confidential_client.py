from globus_sdk.authorizers import BasicAuthorizer
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
