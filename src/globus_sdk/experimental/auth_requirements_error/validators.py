from __future__ import annotations

import typing as t
from contextlib import suppress

T = t.TypeVar("T")


def _string(value: t.Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Must be a string")

    return value


def _string_literal(literal: str) -> t.Callable[[t.Any], str]:
    def validator(value: t.Any) -> str:
        value = _string(value)
        if value != literal:
            raise ValueError(f"Must be '{literal}'")

        return t.cast(str, value)

    return validator


def _class_instance(cls: t.Type[T]) -> t.Callable[[t.Any], T]:
    def validator(value: t.Any) -> T:
        if not isinstance(value, cls):
            raise ValueError(f"Must be an instance of {cls.__name__}")

        return value

    return validator


def _list_of_strings(value: t.Any) -> list[str]:
    if not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
        raise ValueError("Must be a list of strings")

    return value


def _comma_delimited_strings(value: t.Any) -> list[str]:
    if not isinstance(value, str):
        raise ValueError("Must be a comma-delimited string")

    return value.split(",")


def _boolean(value: t.Any) -> bool:
    if not isinstance(value, bool):
        raise ValueError("Must be a bool")

    return value


def _null(value: t.Any) -> None:
    if value is not None:
        raise ValueError("Must be null")

    return None


def _anyof(
    validators: tuple[t.Callable[..., t.Any], ...],
    description: str,
) -> t.Callable[..., t.Any]:
    def _anyof_validator(value: t.Any) -> t.Any:
        for validator in validators:
            with suppress(ValueError):
                return validator(value)

        raise ValueError(f"Must be {description}")

    return _anyof_validator


String: t.Callable[[t.Any], str] = _string
StringLiteral: t.Callable[[str], t.Callable[[t.Any], str]] = _string_literal
ClassInstance: t.Callable[[t.Any], t.Any] = _class_instance
ListOfStrings: t.Callable[[t.Any], list[str]] = _list_of_strings
CommaDelimitedStrings: t.Callable[[t.Any], list[str]] = _comma_delimited_strings
Bool: t.Callable[[t.Any], bool] = _boolean
Null: t.Callable[[t.Any], None] = _null
OptionalString: t.Callable[[t.Any], str | None] = _anyof(
    (_string, _null), description="a string or null"
)
OptionalListOfStrings: t.Callable[[t.Any], list[str] | None] = _anyof(
    (_list_of_strings, _null), description="a list of strings or null"
)
OptionalCommaDelimitedStrings: t.Callable[[t.Any], list[str] | None] = _anyof(
    (_comma_delimited_strings, _null), description="a comma-delimited string or null"
)
OptionalListOfStringsOrCommaDelimitedStrings: t.Callable[
    [t.Any], list[str] | None
] = _anyof(
    (_list_of_strings, _comma_delimited_strings, _null),
    description="a list of strings, a comma-delimited string, or null",
)
OptionalBool: t.Callable[[t.Any], bool | None] = _anyof(
    (_boolean, _null), description="a bool or null"
)
