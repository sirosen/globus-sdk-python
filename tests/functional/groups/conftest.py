import pytest

import globus_sdk


@pytest.fixture
def groups_client(no_retry_policy):
    class CustomGroupsClient(globus_sdk.GroupsClient):
        retry_policy = no_retry_policy

    return CustomGroupsClient()
