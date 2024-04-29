import uuid

from globus_sdk import AuthClient, Scope

# setup: get a consent forest
ac = AuthClient()
identity_id = uuid.uuid1()
consents = ac.get_consents(identity_id)
consent_forest = consents.to_forest()

# create some variant types
xfer_str: str = "urn:globus:auth:scope:transfer.api.globus.org:all"
strlist: list[str] = [xfer_str]
scopelist: list[Scope] = Scope.parse(xfer_str)

# all should be allowed
b: bool
b = consent_forest.meets_scope_requirements(xfer_str)
b = consent_forest.meets_scope_requirements((xfer_str,))
b = consent_forest.meets_scope_requirements(strlist)
b = consent_forest.meets_scope_requirements(scopelist)

# and we really are validating the type, since a bool or list[bool] is not allowed
consent_forest.meets_scope_requirements(b)  # type: ignore[arg-type]
blist: list[bool] = [b]
consent_forest.meets_scope_requirements(blist)  # type: ignore[arg-type]
