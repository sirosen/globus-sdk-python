import pytest
import responses


def test_cannot_encode_dict_as_text(client):
    with pytest.raises(TypeError):
        client.post("/bar", data={"baz": 1}, encoding="text")


def test_cannot_encode_with_unknown_encoding(client):
    with pytest.raises(ValueError):
        client.post("/bar", data={"baz": 1}, encoding="some-random-string")


def test_cannot_form_encode_bad_types(client):
    with pytest.raises(TypeError):
        client.post("/bar", data=["baz", "buzz"], encoding="form")
    with pytest.raises(TypeError):
        client.post("/bar", data=1, encoding="form")


def test_form_encoding_works(client):
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data={"baz": 1}, encoding="form")

    last_req = responses.calls[-1].request
    assert last_req.body == "baz=1"


def test_text_encoding_sends_ascii_string(client):
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data="baz", encoding="text")

    last_req = responses.calls[-1].request
    assert last_req.body == "baz"


def test_text_encoding_can_send_non_ascii_utf8_bytes(client):
    # this test is a reproducer for an issue in which attempting to send these bytes
    # in the form of a (decoded) string would fail, as urllib3 tried to encode them as
    # latin-1 bytes incorrectly
    # passing the bytes already UTF-8 encoded should work
    responses.add(responses.POST, "https://foo.api.globus.org/bar", body="hi")
    client.post("/bar", data='{"field“: "value“}'.encode(), encoding="text")

    last_req = responses.calls[-1].request
    assert last_req.body == '{"field“: "value“}'.encode()
