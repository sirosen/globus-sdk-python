import globus_sdk
from globus_sdk.services.auth._common import SupportsJWKMethods

# setup clients
ac = globus_sdk.AuthClient()
nc = globus_sdk.NativeAppAuthClient("foo_client_id")
cc = globus_sdk.ConfidentialAppAuthClient("foo_client_id", "foo_client_secret")

# check that each one supports the JWK methods
x: SupportsJWKMethods
x = ac
x = nc
x = cc
