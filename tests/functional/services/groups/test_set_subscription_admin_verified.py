import json
import re

import pytest

from globus_sdk import RemovedInV4Warning
from globus_sdk._testing import get_last_request, load_response


def test_set_subscription_admin_verified(groups_client):
    meta = load_response(groups_client.set_subscription_admin_verified).metadata

    res = groups_client.set_subscription_admin_verified(
        group_id=meta["group_id"],
        subscription_id=meta["subscription_id"],
    )
    assert res.http_status == 200
    assert res.data["group_id"] == meta["group_id"]
    assert res.data["subscription_admin_verified_id"] == meta["subscription_id"]

    req = get_last_request()
    req = json.loads(req.body)
    assert req == {"subscription_admin_verified_id": meta["subscription_id"]}


def test_set_subscription_admin_verified_id(groups_client):
    """Test that the deprecated alias warns but is functionally equivalent."""
    meta = load_response(groups_client.set_subscription_admin_verified).metadata

    with pytest.warns(
        RemovedInV4Warning,
        match=re.escape(
            "`GroupsClient.set_subscription_admin_verified_id()` has been renamed to "
            "`GroupsClient.set_subscription_admin_verified()`."
        ),
    ):
        res = groups_client.set_subscription_admin_verified_id(
            group_id=meta["group_id"],
            subscription_id=meta["subscription_id"],
        )
    assert res.http_status == 200
    assert res.data["group_id"] == meta["group_id"]
    assert res.data["subscription_admin_verified_id"] == meta["subscription_id"]

    req = get_last_request()
    req = json.loads(req.body)
    assert req == {"subscription_admin_verified_id": meta["subscription_id"]}
