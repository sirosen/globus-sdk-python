"""
Tests for submitting Transfer and Delete tasks
"""
import pytest
import six

import globus_sdk
from tests.common import GO_EP1_ID, GO_EP2_ID, register_api_route

TRANSFER_SUBMISSION_NODATA_ERROR = """{
  "code": "ClientError.BadRequest.NoTransferItems",
  "message": "A transfer requires at least one item",
  "request_id": "oUAA6Sq2P",
  "resource": "/transfer"
}"""

TRANSFER_SUBMISSION_SUCCESS = """{
  "DATA_TYPE": "transfer_result",
  "code": "Accepted",
  "message": "The transfer has been accepted and a task has been created and queued for execution",
  "request_id": "7HgMVYazI",
  "resource": "/transfer",
  "submission_id": "foosubmitid",
  "task_id": "f51bdaea-ad78-11e8-823c-0a3b7ca8ce66",
  "task_link": {
    "DATA_TYPE": "link",
    "href": "task/f51bdaea-ad78-11e8-823c-0a3b7ca8ce66?format=json",
    "rel": "related",
    "resource": "task",
    "title": "related task"
  }
}"""  # noqa


DELETE_SUBMISSION_SUCCESS = """{
  "DATA_TYPE": "delete_result",
  "code": "Accepted",
  "message": "The delete has been accepted and a task has been created and queued for execution",
  "request_id": "NS2QXhLZ7",
  "resource": "/delete",
  "submission_id": "foosubmitid",
  "task_id": "b5370336-ad79-11e8-823c-0a3b7ca8ce66",
  "task_link": {
    "DATA_TYPE": "link",
    "href": "task/b5370336-ad79-11e8-823c-0a3b7ca8ce66?format=json",
    "rel": "related",
    "resource": "task",
    "title": "related task"
  }
}"""  # noqa


@pytest.fixture
def mock_submission_id():
    register_api_route("transfer", "/submission_id", body='{"value": "foosubmitid"}')


@pytest.fixture
def transfer_data(client, mock_submission_id):
    def _transfer_data(**kwargs):
        return globus_sdk.TransferData(client, GO_EP1_ID, GO_EP2_ID, **kwargs)

    return _transfer_data


@pytest.fixture
def delete_data(client, mock_submission_id):
    def _delete_data(**kwargs):
        return globus_sdk.DeleteData(client, GO_EP1_ID, **kwargs)

    return _delete_data


def test_transfer_submit_failure(client, transfer_data):
    register_api_route(
        "transfer",
        "/transfer",
        method="POST",
        status=400,
        body=TRANSFER_SUBMISSION_NODATA_ERROR,
    )

    with pytest.raises(globus_sdk.TransferAPIError) as excinfo:
        client.submit_transfer(transfer_data())

    assert excinfo.value.http_status == 400
    assert excinfo.value.request_id == "oUAA6Sq2P"
    assert excinfo.value.code == "ClientError.BadRequest.NoTransferItems"


def test_transfer_submit_success(client, transfer_data):
    register_api_route(
        "transfer", "/transfer", method="POST", body=TRANSFER_SUBMISSION_SUCCESS
    )

    tdata = transfer_data(
        label="mytask", sync_level="exists", deadline="2018-06-01", custom_param="foo"
    )
    assert tdata["custom_param"] == "foo"
    assert tdata["sync_level"] == 0

    tdata.add_item(six.b("/path/to/foo"), six.u("/path/to/bar"))
    tdata.add_symlink_item("linkfoo", "linkbar")

    res = client.submit_transfer(tdata)

    assert res
    assert res["submission_id"] == "foosubmitid"
    assert res["task_id"] == "f51bdaea-ad78-11e8-823c-0a3b7ca8ce66"


def test_delete_submit_success(client, delete_data):
    register_api_route(
        "transfer", "/delete", method="POST", body=DELETE_SUBMISSION_SUCCESS
    )

    ddata = delete_data(label="mytask", deadline="2018-06-01", custom_param="foo")
    assert ddata["custom_param"] == "foo"

    ddata.add_item("/path/to/foo")

    res = client.submit_delete(ddata)

    assert res
    assert res["submission_id"] == "foosubmitid"
    assert res["task_id"] == "b5370336-ad79-11e8-823c-0a3b7ca8ce66"
