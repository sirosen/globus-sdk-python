import pytest

import globus_sdk


@pytest.fixture
def client(no_retry_policy):
    class CustomTransferClient(globus_sdk.TransferClient):
        retry_policy = no_retry_policy

    return CustomTransferClient()
