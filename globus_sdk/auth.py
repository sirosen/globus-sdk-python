from __future__ import print_function

import urllib

from globus_sdk.base import BaseClient


class AuthClient(BaseClient):
    def __init__(self, environment="default"):
        BaseClient.__init__(self, "auth", environment)

    def get_identities(self, **kw):
        return self.get("/v2/identities", params=kw)

    def token_introspect(self, token, **kw):
        post_data = dict(token=token)
        post_data.update(kw)
        string_data = urllib.urlencode(post_data)
        return self.post("/v2/oauth2/token/introspect", data=string_data)
