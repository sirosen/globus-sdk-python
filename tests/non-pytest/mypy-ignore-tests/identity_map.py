# check IdentityMap usages
import globus_sdk

# create clients for later usage
ac = globus_sdk.AuthClient()
nc = globus_sdk.NativeAppAuthClient("foo_client_id")
cc = globus_sdk.ConfidentialAppAuthClient("foo_client_id", "foo_client_secret")

# check init allows the service client but not the login clients
im = globus_sdk.IdentityMap(ac)
im = globus_sdk.IdentityMap(cc)  # type: ignore[arg-type]
im = globus_sdk.IdentityMap(nc)  # type: ignore[arg-type]

# getitem and delitem work, but setitem and contains do not
foo = im["foo"]
del im["foo"]
im["foo"] = "bar"  # type: ignore[index]
somebool = "foo" in im  # type: ignore[operator]
