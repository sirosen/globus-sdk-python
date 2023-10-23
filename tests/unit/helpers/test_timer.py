import pytest

from globus_sdk import TimerJob, TransferData, TransferTimer, exc
from tests.common import GO_EP1_ID, GO_EP2_ID


def test_timer_from_transfer_data_ok():
    tdata = TransferData(None, GO_EP1_ID, GO_EP2_ID)
    with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
        job = TimerJob.from_transfer_data(tdata, "2022-01-01T00:00:00Z", 600)
    assert "callback_body" in job
    assert "body" in job["callback_body"]
    assert "source_endpoint" in job["callback_body"]["body"]
    assert "destination_endpoint" in job["callback_body"]["body"]
    assert job["callback_body"]["body"]["source_endpoint"] == GO_EP1_ID
    assert job["callback_body"]["body"]["destination_endpoint"] == GO_EP2_ID


@pytest.mark.parametrize(
    "badkey, value", (("submission_id", "foo"), ("skip_activation_check", True))
)
def test_timer_from_transfer_data_rejects_forbidden_keys(badkey, value):
    tdata = TransferData(None, GO_EP1_ID, GO_EP2_ID, **{badkey: value})
    with pytest.raises(ValueError):
        with pytest.warns(exc.RemovedInV4Warning, match="Prefer TransferTimer"):
            TimerJob.from_transfer_data(tdata, "2022-01-01T00:00:00Z", 600)


def test_transfer_timer_ok():
    tdata = TransferData(source_endpoint=GO_EP1_ID, destination_endpoint=GO_EP2_ID)
    timer = TransferTimer(body=tdata, name="foo timer", schedule={"type": "once"})
    assert timer["name"] == "foo timer"
    assert timer["schedule"]["type"] == "once"
    assert {"source_endpoint", "destination_endpoint"} < timer["body"].keys()
    assert timer["body"]["source_endpoint"] == GO_EP1_ID
    assert timer["body"]["destination_endpoint"] == GO_EP2_ID


def test_transfer_timer_removes_disallowed_fields():
    # set transfer-data-like body with disallowed fields
    tdata = {"submission_id": "foo", "skip_activation_check": False, "foo": "bar"}
    timer = TransferTimer(body=tdata, name="foo timer", schedule={"type": "once"})
    assert timer["name"] == "foo timer"
    assert timer["schedule"]["type"] == "once"

    # confirm that disallowed fields are stripped in the timer,
    # but the original dict is unchanged
    assert timer["body"] == {"foo": "bar"}
    assert set(tdata.keys()) == {"submission_id", "skip_activation_check", "foo"}
