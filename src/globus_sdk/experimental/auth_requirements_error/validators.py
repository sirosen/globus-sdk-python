from __future__ import annotations

import inspect
import sys
import typing as t
from contextlib import suppress

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

T = t.TypeVar("T", covariant=True)


# NB: the type parameter of a Validator is what it *produces*
# meaning that a validator which converts `"foo,bar"` to `["foo", "bar"]` should
# be typed with `T=list[str]`, not `T=str`
class Validator(Protocol[T]):
    def __call__(self, name: str, value: t.Any) -> T:
        ...


class HasErrorMessage(Protocol):
    error_message: str


def _fail(o: HasErrorMessage, name: str) -> t.NoReturn:
    raise ValueError(f"Error validating field '{name}': {o.error_message}")


class _String(Validator[str]):
    error_message = "must be a string"

    def __call__(self, name: str, value: t.Any) -> str:
        if not isinstance(value, str):
            _fail(self, name)

        return value


String = _String()


class StringLiteral(Validator[T]):
    def __init__(self, literal: str) -> None:
        self._value = literal
        self.error_message = f"must be '{literal}'"

    def __call__(self, name: str, value: t.Any) -> T:
        value = String(name, value)
        if value != self._value:
            _fail(self, name)
        return t.cast(T, value)


class IsInstance(Validator[T]):
    def __init__(self, cls: t.Type[T]) -> None:
        self._cls = cls
        self.error_message = f"must be an instance of {self._cls.__name__}"

    def __call__(self, name: str, value: t.Any) -> T:
        if not isinstance(value, self._cls):
            _fail(self, name)

        return value


class _ListOfStrings(Validator[t.List[str]]):
    error_message = "must be a list of strings"

    def __call__(self, name: str, value: t.Any) -> t.List[str]:
        if not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
            _fail(self, name)

        return value


ListOfStrings = _ListOfStrings()


class _CommaDelimitedStrings(Validator[t.List[str]]):
    error_message = "must be a comma-delimited of string"

    def __call__(self, name: str, value: t.Any) -> t.List[str]:
        if not isinstance(value, str):
            _fail(self, name)

        return value.split(",")


CommaDelimitedStrings = _CommaDelimitedStrings()


class _Boolean(Validator[bool]):
    error_message = "must be a bool"

    def __call__(self, name: str, value: t.Any) -> bool:
        if not isinstance(value, bool):
            _fail(self, name)

        return value


Boolean = _Boolean()


class _Null(Validator[None]):
    error_message = "must be null"

    def __call__(self, name: str, value: t.Any) -> None:
        if value is not None:
            _fail(self, name)

        return None


Null = _Null()


class _AnyOf(Validator[t.Any]):
    def __init__(self, *validators: Validator[t.Any], description: str) -> None:
        self._validators = validators
        self.error_message = f"must be one {description}"

    def __call__(self, name: str, value: t.Any) -> t.Any:
        for validator in self._validators:
            with suppress(ValueError):
                return validator(name, value)

        _fail(self, name)


OptionalString: Validator[str | None] = _AnyOf(
    String, Null, description="a string or null"
)
OptionalListOfStrings: Validator[list[str] | None] = _AnyOf(
    ListOfStrings, Null, description="a list of strings or null"
)
OptionalCommaDelimitedStrings: Validator[list[str] | None] = _AnyOf(
    CommaDelimitedStrings, Null, description="a comma-delimited string or null"
)
OptionalListOfStringsOrCommaDelimitedStrings: Validator[list[str] | None] = _AnyOf(
    ListOfStrings,
    CommaDelimitedStrings,
    Null,
    description="a list of strings, a comma-delimited string, or null",
)
OptionalBool: Validator[bool | None] = _AnyOf(
    Boolean, Null, description="a bool or null"
)


def require_at_least_one_field(o: object, field_description: str) -> None:
    one_of_fields = set(derive_supported_fields(o))
    if all((getattr(o, field_name) is None) for field_name in one_of_fields):
        raise ValueError(
            f"Must include at least one {field_description}: "
            + ", ".join(one_of_fields)
        )


def derive_supported_fields(o_or_cls: object | type) -> list[str]:
    # mypy warns here about `__init__` access being potnetially unsound, but the check
    # is a false negative in this case since we're operating on a closed set of classes
    # which we control
    signature = inspect.signature(o_or_cls.__init__)  # type: ignore[misc]
    return [k for k in signature.parameters.keys() if k not in ("extra", "self")]
