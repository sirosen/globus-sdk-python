from __future__ import print_function

from six.moves.urllib.parse import urlencode

from globus_sdk import config
from globus_sdk.base import BaseClient, merge_params


class AuthClient(BaseClient):
    def __init__(self, environment=config.get_default_environ(), token=None,
                 app_name=None):
        """
        Client for the
        `Globus Auth API <https://docs.globus.org/api/auth/>`_

        This class provides helper methods for most common resources in the
        Auth API, and the common low-level interface from
        :class:`BaseClient <globus_sdk.base.BaseClient>`
        """
        BaseClient.__init__(self, "auth", environment, token=token,
                            app_name=app_name)

    def get_identities(self, **params):
        """
        GET /v2/api/identities
        """
        return self.get("/v2/api/identities", params=params)

    def token_introspect(self, token, **kw):
        """
        POST /v2/oauth2/token/introspect

        Get information about a Globus Auth token. Requires basic auth
        using oauth client credentials, where username=client_id
        and password=client_secret.
        """
        merge_params(kw, token=token)
        return self.post("/v2/oauth2/token/introspect",
                         text_body=urlencode(kw))

    def config_load_token(self):
        return config.get_auth_token(self.environment)
