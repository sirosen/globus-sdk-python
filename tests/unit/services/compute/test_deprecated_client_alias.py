import pytest

import globus_sdk
from globus_sdk import ComputeClientV2, RemovedInV4Warning


def test_legacy_client_warns_on_import():
    from globus_sdk.services.compute import (
        deprecated_client as deprecated_client_module,
    )

    # first, remove the object from the module's `__dict__` if it was there
    # ensures that access will run `__getattr__`
    if "ComputeClient" in deprecated_client_module.__dict__:
        del deprecated_client_module.__dict__["ComputeClient"]
    # and, similarly, remove it from 'globus_sdk'
    if "ComputeClient" in globus_sdk.__dict__:
        del globus_sdk.__dict__["ComputeClient"]

    with pytest.warns(RemovedInV4Warning, match="deprecated"):
        from globus_sdk import ComputeClient  # noqa: F401


@pytest.mark.filterwarnings("ignore::globus_sdk.RemovedInV4Warning")
def test_legacy_client_is_v2():
    client = globus_sdk.ComputeClient()
    assert isinstance(client, ComputeClientV2)
