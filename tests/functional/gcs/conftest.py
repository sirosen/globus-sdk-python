import pytest

from globus_sdk import GCSClient


@pytest.fixture
def client():
    # default fqdn for GCS client testing
    return GCSClient("abc.xyz.data.globus.org")
