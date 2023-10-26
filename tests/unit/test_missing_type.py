import copy
import pickle

import pytest

from globus_sdk import utils


def test_missing_type_cannot_be_instantiated():
    with pytest.raises(TypeError, match="MissingType should not be instantiated"):
        utils.MissingType()


def test_missing_sentinel_bools_as_false():
    assert bool(utils.MISSING) is False


def test_str_of_missing():
    assert str(utils.MISSING) == "<globus_sdk.MISSING>"


def test_copy_of_missing_is_self():
    assert copy.copy(utils.MISSING) is utils.MISSING
    assert copy.deepcopy(utils.MISSING) is utils.MISSING


def test_pickle_of_missing_is_self():
    assert pickle.loads(pickle.dumps(utils.MISSING)) is utils.MISSING
