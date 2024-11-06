from globus_sdk.services.compute.client import ComputeClient, ComputeClientV2


def test_canonical_client_is_v2():
    client = ComputeClient()
    assert isinstance(client, ComputeClientV2)
