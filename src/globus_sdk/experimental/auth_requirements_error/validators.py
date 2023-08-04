from __future__ import annotations

import sys
import typing as t
from contextlib import suppress

if sys.version_info >= (3, 9):
    from typing import get_type_hints
else:
    from typing_extensions import get_type_hints

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


def run_annotated_validators(o: object, require_at_least_one: bool = False) -> None:
    found_non_null = False
    validator_annotations = list(get_validator_annotations(o))

    for attrname, value in validator_annotations:
        try:
            validator_result = value(getattr(o, attrname))
        except ValueError as e:
            raise ValueError(f"Error validating field '{attrname}': {e}") from e
        setattr(o, attrname, validator_result)
        if validator_result is not None:
            found_non_null = True

    if require_at_least_one and not found_non_null:
        raise ValueError(
            "Must include at least one supported parameter: "
            + ", ".join([f for f, _ in validator_annotations])
        )


def get_supported_fields(o_or_cls: object | type) -> list[str]:
    return [field_name for (field_name, _) in get_validator_annotations(o_or_cls)]


def get_validator_annotations(
    o_or_cls: object | type,
) -> t.Iterator[tuple[str, t.Callable[..., t.Any]]]:
    if isinstance(o_or_cls, type):
        cls = o_or_cls
    else:
        cls = o_or_cls.__class__

    for attrname, value in get_type_hints(cls, include_extras=True).items():
        # an Annotated[...] annotation produces a special form "_AnnotatedAlias"
        # rather than inspecting typing internals, check that the interface we want
        # (`__metadata__` is present and is a tuple) is satisfied by the annotation
        if not isinstance(getattr(value, "__metadata__", None), tuple):
            continue

        maybe_validator = value.__metadata__[0]
        if not callable(maybe_validator):
            continue

        yield (attrname, maybe_validator)
