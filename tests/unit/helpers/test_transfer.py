import pytest

import globus_sdk
from tests.common import GO_EP1_ID, GO_EP2_ID


@pytest.fixture
def client():
    def _mock_submission_id(*args, **kwargs):
        return {"value": "fooid"}

    tc = globus_sdk.TransferClient()
    tc.get_submission_id = _mock_submission_id

    return tc


@pytest.fixture
def transfer_data(client):
    def _transfer_data(**kwargs):
        return globus_sdk.TransferData(client, GO_EP1_ID, GO_EP2_ID, **kwargs)

    return _transfer_data


@pytest.fixture
def delete_data(client):
    def _delete_data(**kwargs):
        return globus_sdk.DeleteData(client, GO_EP1_ID, **kwargs)

    return _delete_data


def test_tranfer_init(transfer_data):
    """
    Creates TransferData objects with and without parameters,
    Verifies TransferData field initialization
    """
    # default init
    tdata = transfer_data()
    assert tdata["DATA_TYPE"] == "transfer"
    assert tdata["source_endpoint"] == GO_EP1_ID
    assert tdata["destination_endpoint"] == GO_EP2_ID
    assert "submission_id" in tdata
    assert "DATA" in tdata
    assert len(tdata["DATA"]) == 0

    # init with params
    label = "label"
    params = {"param1": "value1", "param2": "value2"}
    param_tdata = transfer_data(
        label=label, sync_level="exists", additional_fields=params
    )
    assert param_tdata["label"] == label
    # sync_level of "exists" should be converted to 0
    assert param_tdata["sync_level"] == 0
    for par in params:
        assert param_tdata[par] == params[par]


def test_transfer_add_item(transfer_data):
    """
    Adds three items to TransferData, verifies results
    """
    tdata = transfer_data()
    # add item
    source_path = "source/path/"
    dest_path = "dest/path/"
    tdata.add_item(source_path, dest_path)
    # verify results
    assert len(tdata["DATA"]) == 1
    data = tdata["DATA"][0]
    assert data["DATA_TYPE"] == "transfer_item"
    assert data["source_path"] == source_path
    assert data["destination_path"] == dest_path
    assert not data["recursive"]
    assert data["external_checksum"] is None
    assert data["checksum_algorithm"] is None

    # add recursive item
    tdata.add_item(source_path, dest_path, recursive=True)
    # verify results
    assert len(tdata["DATA"]) == 2
    r_data = tdata["DATA"][1]
    assert r_data["DATA_TYPE"] == "transfer_item"
    assert r_data["source_path"] == source_path
    assert r_data["destination_path"] == dest_path
    assert r_data["recursive"]
    assert r_data["external_checksum"] is None
    assert r_data["checksum_algorithm"] is None

    checksum = "d577273ff885c3f84dadb8578bb41399"
    algorithm = "MD5"
    tdata.add_item(
        source_path, dest_path, external_checksum=checksum, checksum_algorithm=algorithm
    )
    assert len(tdata["DATA"]) == 3
    c_data = tdata["DATA"][2]
    assert c_data["DATA_TYPE"] == "transfer_item"
    assert c_data["source_path"] == source_path
    assert c_data["destination_path"] == dest_path
    assert not c_data["recursive"]
    assert c_data["external_checksum"] == checksum
    assert c_data["checksum_algorithm"] == algorithm


def test_transfer_add_symlink_item(transfer_data):
    """
    Adds a transfer_symlink_item to TransferData, verifies results
    """
    tdata = transfer_data()
    # add item
    source_path = "source/path/"
    dest_path = "dest/path/"
    tdata.add_symlink_item(source_path, dest_path)
    # verify results
    assert len(tdata["DATA"]) == 1
    data = tdata["DATA"][0]
    assert data["DATA_TYPE"] == "transfer_symlink_item"
    assert data["source_path"] == source_path
    assert data["destination_path"] == dest_path


def test_delete_init(delete_data):
    """
    Verifies DeleteData field initialization
    """
    # default init
    default_ddata = delete_data()
    assert default_ddata["DATA_TYPE"] == "delete"
    assert default_ddata["endpoint"] == GO_EP1_ID
    assert "submission_id" in default_ddata
    assert "DATA" in default_ddata
    assert len(default_ddata["DATA"]) == 0

    # init with params
    label = "label"
    params = {"param1": "value1", "param2": "value2"}
    param_ddata = delete_data(label=label, recursive="True", additional_fields=params)
    assert param_ddata["label"] == label
    assert param_ddata["recursive"] == "True"
    for par in params:
        assert param_ddata[par] == params[par]


def test_delete_add_item(delete_data):
    """
    Adds an item to DeleteData, verifies results
    """
    ddata = delete_data()
    # add item
    path = "source/path/"
    ddata.add_item(path)
    # verify results
    assert len(ddata["DATA"]) == 1
    data = ddata["DATA"][0]
    assert data["DATA_TYPE"] == "delete_item"
    assert data["path"] == path


def test_delete_iter_items(delete_data):
    ddata = delete_data()
    # add item
    ddata.add_item("abc/")
    ddata.add_item("def/")

    # order preserved, well-formed
    as_list = list(ddata.iter_items())
    assert len(as_list) == 2

    def check_item(x, path):
        assert isinstance(x, dict)
        assert x.get("DATA_TYPE") == "delete_item"
        assert x.get("path") == path

    check_item(as_list[0], "abc/")
    check_item(as_list[1], "def/")


def test_transfer_iter_items(transfer_data):
    tdata = transfer_data()
    tdata.add_item("source/abc.txt", "dest/abc.txt")
    tdata.add_item("source/def/", "dest/def/", recursive=True)

    # order preserved, well-formed
    as_list = list(tdata.iter_items())
    assert len(as_list) == 2

    def check_item(x, src, dst, params=None):
        params = params or {}
        assert isinstance(x, dict)
        assert x.get("DATA_TYPE") == "transfer_item"
        assert x.get("source_path") == src
        assert x.get("destination_path") == dst
        for k, v in params.items():
            assert x.get(k) == v

    check_item(as_list[0], "source/abc.txt", "dest/abc.txt")
    check_item(as_list[1], "source/def/", "dest/def/", {"recursive": True})
