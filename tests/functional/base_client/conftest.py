from unittest import mock

import pytest

import globus_sdk


@pytest.fixture(autouse=True)
def mocksleep():
    with mock.patch("time.sleep") as m:
        yield m


@pytest.fixture
def client():
    class CustomClient(globus_sdk.base.BaseClient):
        service_name = "foo"

    return CustomClient()
