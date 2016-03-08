from __future__ import print_function

import requests

from globus_sdk.base import BaseClient
from globus_sdk import config


NEXUS_TOKEN_PATH = "/goauth/token?grant_type=client_credentials"


class TransferClient(BaseClient):
    def __init__(self, environment="default"):
        BaseClient.__init__(self, "transfer", environment, "/v0.10/")

    def get_goauth_token(self, username, password):
        """
        Legacy method for getting a GOAuth token from nexus using
        globusid username and password. Clients using this should
        be prepared to migrate to Globus Auth.

        Note that these tokens have a long lifetime and should be saved
        and re-used.

        TODO: should this live somewhere else? It's temporary anyway, so
        maybe doesn't matter?
        """
        nexus_url = config.get_service_url(self.environment, "nexus")
        url = "https://%s%s" % (nexus_url, NEXUS_TOKEN_PATH)
        headers = dict(Accepts="application/json")
        r = requests.get(url, auth=(username, password),
                         headers=headers, verifyf=self._verify)
        data = r.json()
        return data["access_token"]

    # Convenience methods, providing more pythonic access to common REST
    # resources
    # TODO: Is there consensus that we want to maintain these? I feel
    # strongly that we shouldn't provide anything more complex, e.g.
    # hard coding param names and document types, but wouldn't be too
    # bad to maintain these.
    def get_endpoint(self, endpoint_id, **kw):
        """GET /endpoint/<endpoint_id>"""
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.get(path, params=kw)

    def update_endpoint(self, endpoint_id, data, **kw):
        """PUT /endpoint/<endpoint_id>"""
        path = self.qjoin_path("endpoint", endpoint_id)
        return self.put(path, data, params=kw)

    def create_endpoint(self, data):
        """POST /endpoint/<endpoint_id>"""
        return self.post("endpoint", data)


def _get_client_from_args():
    import sys

    if len(sys.argv) < 2:
        print("Usage: %s token_file [environment]" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1]) as f:
        token = f.read().strip()

    if len(sys.argv) > 2:
        environment = sys.argv[2]
    else:
        environment = "default"

    api = TransferClient(environment)
    api.set_auth_token(token)
    return api


if __name__ == '__main__':
    api = _get_client_from_args()
