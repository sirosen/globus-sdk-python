import uuid

import pytest

from globus_sdk import _guards, exc


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        ([], str, True),
        ([1, 2], int, True),
        (["1", ""], str, True),
        ([], list, True),
        ([[], [1, 2], ["foo"]], list, True),
        # failing
        ([1], str, False),
        (["foo"], int, False),
        ((1, 2), int, False),
        (list, list, False),
        (list, str, False),
        (["foo", 1], str, False),
        ([1, 2], list, False),
    ],
)
def test_list_of_guard(value, typ, ok):
    assert _guards.is_list_of(value, typ) == ok


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        (None, str, True),
        ("foo", str, True),
        # failing
        (b"foo", str, False),
        ("", int, False),
        (type(None), str, False),
    ],
)
def test_opt_guard(value, typ, ok):
    assert _guards.is_optional(value, typ) == ok


@pytest.mark.parametrize(
    "value, typ, ok",
    [
        # passing
        ([], str, True),
        ([], int, True),
        ([1, 2], int, True),
        (["1", ""], str, True),
        (None, str, True),
        # failing
        # NB: the guard checks `list[str] | None`, not `list[str | None]`
        ([None], str, False),
        (b"foo", str, False),
        ("", str, False),
        (type(None), str, False),
    ],
)
def test_opt_list_guard(value, typ, ok):
    assert _guards.is_optional_list_of(value, typ) == ok


@pytest.mark.parametrize("value", (uuid.UUID(int=0), str(uuid.UUID(int=1))))
def test_uuidlike_ok(value):
    assert _guards.validators.uuidlike("foo", value) == value


@pytest.mark.parametrize("value", (str(uuid.UUID(int=0))[:-1], ""))
def test_uuidlike_fails_value(value):
    with pytest.raises(
        exc.ValidationError, match="'foo' must be a valid UUID"
    ) as excinfo:
        _guards.validators.uuidlike("foo", value)

    err = excinfo.value
    assert f"value='{value}'" in str(err)


@pytest.mark.parametrize("value", (object(), None, ["bar"]))
def test_uuidlike_fails_type(value):
    with pytest.raises(
        exc.ValidationError, match="'foo' must be a UUID or str"
    ) as excinfo:
        _guards.validators.uuidlike("foo", value)

    err = excinfo.value
    assert f"value='{value}'" in str(err)


@pytest.mark.parametrize(
    "validator, value",
    (
        pytest.param(_guards.validators.str_, "bar", id="str"),
        pytest.param(_guards.validators.int_, 0, id="int-0"),
        pytest.param(_guards.validators.int_, 1, id="int-1"),
        pytest.param(_guards.validators.opt_str, "bar", id="opt_str-str"),
        pytest.param(_guards.validators.opt_str, None, id="opt_str-None"),
        pytest.param(_guards.validators.opt_bool, True, id="opt_bool-True"),
        pytest.param(_guards.validators.opt_bool, False, id="opt_bool-False"),
        pytest.param(_guards.validators.opt_bool, None, id="opt_bool-None"),
        pytest.param(_guards.validators.str_list, [], id="str_list-empty"),
        pytest.param(_guards.validators.str_list, ["foo"], id="str_list-onestr"),
        pytest.param(_guards.validators.opt_str_list, [], id="opt_str_list-empty"),
        pytest.param(
            _guards.validators.opt_str_list, ["foo"], id="opt_str_list-onestr"
        ),
        pytest.param(_guards.validators.opt_str_list, None, id="opt_str_list-None"),
        pytest.param(
            _guards.validators.opt_str_list_or_commasep,
            [],
            id="opt_str_list_or_commasep-empty",
        ),
        pytest.param(
            _guards.validators.opt_str_list_or_commasep,
            ["foo"],
            id="opt_str_list_or_commasep-onestr",
        ),
        pytest.param(
            _guards.validators.opt_str_list_or_commasep,
            None,
            id="opt_str_list_or_commasep-None",
        ),
    ),
)
def test_simple_validator_passing(validator, value):
    assert validator("foo", value) == value


@pytest.mark.parametrize(
    "validator, value, match_message",
    (
        pytest.param(
            _guards.validators.str_, 1, "'foo' must be a string", id="str-int"
        ),
        pytest.param(
            _guards.validators.str_, False, "'foo' must be a string", id="str-bool"
        ),
        pytest.param(
            _guards.validators.str_, None, "'foo' must be a string", id="str-None"
        ),
        pytest.param(
            _guards.validators.int_, "bar", "'foo' must be an int", id="int-str"
        ),
    ),
)
def test_simple_validator_failing(validator, value, match_message):
    with pytest.raises(exc.ValidationError, match=match_message):
        validator("foo", value)
