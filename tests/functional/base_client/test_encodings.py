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
