import typing

import globus_sdk

# type is (str | None)
s: typing.Optional[str] = globus_sdk.BaseClient.resource_server
i: int = globus_sdk.BaseClient.resource_server  # type: ignore [assignment]

# holds on an instance as well
c = globus_sdk.BaseClient()
s = c.resource_server
i = c.resource_server  # type: ignore [assignment]
