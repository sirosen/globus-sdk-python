import json

import globus_sdk
from globus_sdk._testing import get_last_request, load_response


def test_simple_transfer_timer_creation(client):
    meta = load_response(client.create_timer).metadata
    body = globus_sdk.TransferData(
        source_endpoint=meta["source_endpoint"],
        destination_endpoint=meta["destination_endpoint"],
    )
    body.add_item("/share/godata/file1.txt", "/~/file1.txt")

    schedule = globus_sdk.RecurringTimerSchedule(
        interval_seconds=60, end={"condition": "iterations", "iterations": 3}
    )

    timer = client.create_timer(
        timer=globus_sdk.TransferTimer(body=body, schedule=schedule)
    )
    assert timer["timer"]["job_id"] == meta["timer_id"]

    req = get_last_request()
    sent = json.loads(req.body)
    assert sent["timer"]["schedule"] == {
        "type": "recurring",
        "interval_seconds": 60,
        "end": {"condition": "iterations", "iterations": 3},
    }
    assert sent["timer"]["body"] == {
        k: v for k, v in body.items() if k != "skip_activation_check"
    }
