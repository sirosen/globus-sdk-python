import warnings

from globus_sdk import config, exc
from globus_sdk.base import BaseClient


class NexusClient(BaseClient):
    """
    A client for accessing the (mostly deprecated) Nexus API.
    It is still required for a very limited set of activities -- mostly
    fetching the older style of Globus Access Tokens (GOAuth Tokens).
    """
    _DEPRECATION_TEXT = (
        'Globus Nexus provides access to features of Globus which are '
        'being moved to new services. If you use Nexus, be ready to '
        'transition to the new API after we announce it\'s availability.'
    )

    def __init__(self, environment=config.get_default_environ()):
        BaseClient.__init__(self, "nexus", environment)
        # warn that this class is deprecated upon initialization
        warnings.warn(self._DEPRECATION_TEXT, PendingDeprecationWarning)

    def get_goauth_token(self, username, password):
        """
        Legacy method for getting a GOAuth token from nexus using
        globusid username and password. Clients using this should
        be prepared to migrate to Globus Auth.

        Note that these tokens have a long lifetime and should be saved
        and re-used.
        """
        r = self.get('/goauth/token?grant_type=client_credentials',
                     auth=(username, password))
        try:
            return r.json_body['access_token']
        except KeyError:
            raise exc.GlobusAPIError(r)
        else:
            raise
