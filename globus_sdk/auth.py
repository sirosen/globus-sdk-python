from __future__ import print_function

import urllib

from globus_sdk.base import BaseClient, merge_params


class AuthClient(BaseClient):
    def __init__(self, environment="default"):
        BaseClient.__init__(self, "auth", environment)

    def get_identities(self, **kw):
        return self.get("/v2/api/identities", params=kw).json_body

    def token_introspect(self, token, **kw):
        """
        Get information about a Globus Auth token. Requires basic auth
        using oauth client credentials, where username=client_id
        and password=client_secret.
        """
        merge_params(kw, token=token)
        return self.post("/v2/oauth2/token/introspect",
                         text_body=urllib.urlencode(kw)).json_body
