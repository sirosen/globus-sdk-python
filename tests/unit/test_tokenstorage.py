import json
import time
from unittest import mock

import pytest

from globus_sdk.tokenstorage import MemoryAdapter, SimpleJSONFileAdapter, SQLiteAdapter
from globus_sdk.version import __version__ as sdkversion


def test_sqlite_reading_bad_config():
    adapter = SQLiteAdapter(":memory:")
    # inject bad data (array, needs to be dict)
    # store_config does not check the input type, just uses json.dumps()
    adapter.store_config("foo_conf", [])

    with pytest.raises(ValueError, match="reading config data and got non-dict result"):
        adapter.read_config("foo_conf")


def test_sqlite_reading_bad_token_data():
    adapter = SQLiteAdapter(":memory:")
    # inject bad data (array, needs to be dict)
    adapter._connection.execute(
        """\
INSERT INTO token_storage(namespace, resource_server, token_data_json)
VALUES (?, ?, ?)""",
        (adapter.namespace, "foo_rs", "[]"),
    )
    with pytest.raises(
        ValueError, match="data error: token data was not saved as a dict"
    ):
        adapter.get_token_data("foo_rs")


def test_sqliteadapter_passes_connect_params():
    with pytest.raises(TypeError):
        SQLiteAdapter(":memory:", connect_params={"invalid_kwarg": True})

    SQLiteAdapter(":memory:", connect_params={"timeout": 10})


def test_simplejson_reading_bad_data(tmp_path):
    # non-dict data at root
    foo_file = tmp_path / "foo.json"
    foo_file.write_text('["foobar"]')
    foo_adapter = SimpleJSONFileAdapter(str(foo_file))

    with pytest.raises(ValueError, match="Found non-dict root data while loading"):
        foo_adapter.get_by_resource_server()

    # non-dict data in 'by_rs'

    bar_file = tmp_path / "bar.json"
    bar_file.write_text(
        json.dumps(
            {"by_rs": [], "format_version": "1.0", "globus-sdk.version": sdkversion}
        )
    )
    bar_adapter = SimpleJSONFileAdapter(str(bar_file))

    with pytest.raises(ValueError, match="existing data file is malformed"):
        bar_adapter.get_by_resource_server()


def test_simplejson_reading_unsupported_format_version(tmp_path):
    # data appears valid, but lists a value for "format_version" which instructs the
    # adapter explicitly that it is in a format which is unknown / not supported
    foo_file = tmp_path / "foo.json"
    foo_file.write_text(
        json.dumps(
            {"by_rs": {}, "format_version": "0.0", "globus-sdk.version": sdkversion}
        )
    )
    adapter = SimpleJSONFileAdapter(str(foo_file))

    with pytest.raises(ValueError, match="existing data file is in an unknown format"):
        adapter.get_by_resource_server()


def test_memory_adapter_store_overwrites_only_new_data():
    # setup a mock token response
    expiration_time = int(time.time()) + 3600
    mock_response = mock.Mock()
    mock_response.by_resource_server = {
        "resource_server_1": {
            "access_token": "access_token_1",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "bearer",
        },
        "resource_server_2": {
            "access_token": "access_token_2",
            "expires_in": expiration_time,
            "refresh_token": "refresh_token_2",
            "resource_server": "resource_server_2",
            "scope": "scope2 scope2:0 scope2:1",
            "token_type": "bearer",
        },
    }

    # "store" it in memory
    adapter = MemoryAdapter()
    adapter.store(mock_response)

    # read back a sample piece of data
    fetch1 = adapter.get_token_data("resource_server_1")
    assert fetch1["access_token"] == "access_token_1"

    # "store" a new mock response which overwrites only one piece of data
    mock_response2 = mock.Mock()
    mock_response2.by_resource_server = {
        "resource_server_1": {
            "access_token": "access_token_1_new",
            "expires_at_seconds": expiration_time,
            "refresh_token": "refresh_token_1",
            "resource_server": "resource_server_1",
            "scope": "scope1",
            "token_type": "bearer",
        }
    }
    adapter.store(mock_response2)

    # the overwritten data is updated
    fetch2 = adapter.get_token_data("resource_server_1")
    assert fetch2["access_token"] == "access_token_1_new"

    # but the existing data is preserved
    fetch3 = adapter.get_token_data("resource_server_2")
    assert fetch3["access_token"] == "access_token_2"
