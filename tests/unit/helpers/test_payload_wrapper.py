import pytest

from globus_sdk import utils


def test_payload_preparation_strips_missing_dict():
    original = {"foo": None, "bar": utils.MISSING}
    prepared = utils.PayloadWrapper._prepare(original)
    assert prepared == {"foo": None}


# this is a weird case (not really recommended usage), but we have well defined behavior
# for it, so exercise it here
@pytest.mark.parametrize("type_", (list, tuple))
def test_payload_preparation_strips_missing_list_or_tuple(type_):
    original = type_([None, 1, utils.MISSING, 0])
    prepared = utils.PayloadWrapper._prepare(original)
    assert prepared == [None, 1, 0]


@pytest.mark.parametrize("original", (None, 1, 0, True, False, "foo", object()))
def test_payload_preparation_retains_simple_datatype_identity(original):
    prepared = utils.PayloadWrapper._prepare(original)
    # check not only that the values are equal, but that they pass the identity test
    assert prepared is original


# this test makes sense in the context of the identity test above:
# check that the values are equal, although the type may be reconstructed
@pytest.mark.parametrize("original", (["foo", "bar"], {"foo": "bar"}))
def test_payload_preparation_retains_complex_datatype_equality(original):
    prepared = utils.PayloadWrapper._prepare(original)
    assert prepared == original


def test_payload_preparation_dictifies_wrappers():
    x = utils.PayloadWrapper()
    x["foo"] = 1
    prepared = utils.PayloadWrapper._prepare(x)
    assert prepared == {"foo": 1}
    assert isinstance(prepared, dict)
    assert prepared is not x
    assert not isinstance(prepared, utils.PayloadWrapper)


def test_payload_preparation_recursively_dictifies_wrappers():
    x = utils.PayloadWrapper()
    x["foo"] = 1
    y = utils.PayloadWrapper()
    y["bar"] = x
    y["baz"] = [2, x]
    prepared = utils.PayloadWrapper._prepare(y)
    assert prepared == {"bar": {"foo": 1}, "baz": [2, {"foo": 1}]}
