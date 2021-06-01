import pytest

import globus_sdk


@pytest.fixture
def client():
    class CustomClient(globus_sdk.base.BaseClient):
        service_name = "foo"

    return CustomClient()
