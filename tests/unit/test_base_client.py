import json
import logging.handlers
import uuid

import httpretty
import pytest
import six

import globus_sdk
from globus_sdk.base import BaseClient, merge_params, safe_stringify, slash_join
from tests.common import register_api_route


@pytest.fixture
def auth_client():
    return globus_sdk.NativeAppAuthClient(client_id=uuid.uuid1())


@pytest.fixture
def base_client():
    return BaseClient("transfer", base_path="/v0.10/")


# not particularly special, just a handy array of codes which should raise
# errors when encountered
ERROR_STATUS_CODES = (400, 404, 405, 409, 500, 503)


class testObject(object):
    """test obj for safe_stringify testing"""

    def __str__(self):
        return "1"


def test_client_log_adapter(base_client):
    """
    Logs a test message with the base client's logger,
    Confirms the ClientLogAdapter marks the message with the client
    """
    # make a MemoryHandler for capturing the log in a buffer)
    memory_handler = logging.handlers.MemoryHandler(1028)
    base_client.logger.logger.addHandler(memory_handler)
    base_client.logger.logger.setLevel("INFO")
    # send the test message
    in_msg = "Testing ClientLogAdapter"
    base_client.logger.info(in_msg)
    # confirm results
    out_msg = memory_handler.buffer[0].getMessage()
    expected_msg = "[instance:{}] {}".format(id(base_client), in_msg)
    assert expected_msg == out_msg

    memory_handler.close()


def test_set_app_name(base_client):
    """
    Sets app name, confirms results
    """
    # set app name
    app_name = "SDK Test"
    base_client.set_app_name(app_name)
    # confirm results
    assert base_client.app_name == app_name
    assert base_client._headers["User-Agent"] == "{0}/{1}".format(
        base_client.BASE_USER_AGENT, app_name
    )


def test_qjoin_path(base_client):
    """
    Calls qjoin on parts to form a path, confirms results
    """
    parts = ["SDK", "Test", "Path", "Items"]
    path = base_client.qjoin_path(*parts)
    assert path == "/SDK/Test/Path/Items"


@pytest.mark.parametrize(
    "method, allows_body",
    [("get", False), ("delete", False), ("post", True), ("put", True), ("patch", True)],
)
def test_http_methods(method, allows_body, base_client):
    """
    BaseClient.{get, delete, post, put, patch} on a path does "the right thing"
    Sends a text body or JSON body as requested
    Raises a GlobusAPIError if the response is not a 200

    NOTE: tests sending request bodies even on GET (which
    *shouldn't* have bodies but *may* have them in reality).
    """
    methodname = method.upper()
    resolved_method = getattr(base_client, method)
    register_api_route(
        "transfer", "/madeuppath/objectname", method=methodname, body='{"x": "y"}'
    )

    # client should be able to compose the path itself
    path = base_client.qjoin_path("madeuppath", "objectname")

    # request with no body
    res = resolved_method(path)
    req = httpretty.last_request()

    assert req.method == methodname
    assert req.body == six.b("")
    assert "x" in res
    assert res["x"] == "y"

    if allows_body:
        jsonbody = {"foo": "bar"}
        res = resolved_method(path, json_body=jsonbody)
        req = httpretty.last_request()

        assert req.method == methodname
        assert req.body == six.b(json.dumps(jsonbody))
        assert "x" in res
        assert res["x"] == "y"

        res = resolved_method(path, text_body="abc")
        req = httpretty.last_request()

        assert req.method == methodname
        assert req.body == six.b("abc")
        assert "x" in res
        assert res["x"] == "y"

    # send "bad" request
    for status in ERROR_STATUS_CODES:
        register_api_route(
            "transfer",
            "/madeuppath/objectname",
            method=methodname,
            status=status,
            body='{"x": "y", "code": "ErrorCode", "message": "foo"}',
        )

        with pytest.raises(globus_sdk.GlobusAPIError) as excinfo:
            resolved_method("/madeuppath/objectname")

        assert excinfo.value.http_status == status
        assert excinfo.value.raw_json["x"] == "y"
        assert excinfo.value.code == "ErrorCode"
        assert excinfo.value.message == "foo"


@pytest.mark.parametrize(
    "a, b",
    [(a, b) for a in ["a", "a/"] for b in ["b", "/b"]]
    + [("a/b", c) for c in ["", None]],
)
def test_slash_join(a, b):
    """
    slash_joins a's with and without trailing "/"
    to b's with and without leading "/"
    Confirms all have the same correct slash_join output
    """
    assert slash_join(a, b) == "a/b"


def test_merge_params():
    """
    Merges a base parameter dict with other paramaters, validates results
    Confirms works with explicit dictionaries and arguments
    Confirms new parameters set to None are ignored
    Confirms new parameters overwrite old ones (is this correct?)
    """

    # explicit dictionary merging
    params = {"param1": "value1"}
    extra = {"param2": "value2", "param3": "value3"}
    merge_params(params, **extra)
    expected = {"param1": "value1", "param2": "value2", "param3": "value3"}
    assert params == expected

    # arguments
    params = {"param1": "value1"}
    merge_params(params, param2="value2", param3="value3")
    expected = {"param1": "value1", "param2": "value2", "param3": "value3"}
    assert params == expected

    # ignoring parameters set to none
    params = {"param1": "value1"}
    merge_params(params, param2=None, param3=None)
    expected = {"param1": "value1"}
    assert params == expected

    # existing parameters
    params = {"param": "value"}
    merge_params(params, param="newValue")
    expected = {"param": "newValue"}
    assert params == expected


@pytest.mark.parametrize("value", ["1", str(1), b"1", u"1", 1, testObject()])
def test_safe_stringify(value):
    """
    safe_stringifies strings, bytes, explicit unicode, an int, an object
    and confirms safe_stringify returns utf-8 encoding for all inputs
    """
    safe_value = safe_stringify(value)
    assert safe_value == u"1"
    assert type(safe_value) == six.text_type
