from __future__ import annotations

import sys
import typing as t

if t.TYPE_CHECKING:
    from globus_sdk._serializable import Serializable

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard

T = t.TypeVar("T")
S = t.TypeVar("S", bound="Serializable")


def is_list_of(data: t.Any, typ: type[T]) -> TypeGuard[list[T]]:
    return isinstance(data, list) and all(isinstance(item, typ) for item in data)


def is_optional(data: t.Any, typ: type[T]) -> TypeGuard[T | None]:
    return data is None or isinstance(data, typ)


def is_optional_list_of(data: t.Any, typ: type[T]) -> TypeGuard[list[T] | None]:
    return data is None or (
        isinstance(data, list) and all(isinstance(item, typ) for item in data)
    )


# this class is a namespace, separating validators (which error) from TypeGuards
class validators:
    class ValidationError(ValueError):
        pass

    @staticmethod
    def str_(name: str, value: t.Any) -> str:
        if isinstance(value, str):
            return value
        raise validators.ValidationError(f"'{name}' must be a string")

    @staticmethod
    def int_(name: str, value: t.Any) -> int:
        if isinstance(value, int):
            return value
        raise validators.ValidationError(f"'{name}' must be an int")

    @staticmethod
    def opt_str(name: str, value: t.Any) -> str | None:
        if is_optional(value, str):
            return value
        raise validators.ValidationError(f"'{name}' must be a string or null")

    @staticmethod
    def opt_bool(name: str, value: t.Any) -> bool | None:
        if is_optional(value, bool):
            return value
        raise validators.ValidationError(f"'{name}' must be a bool or null")

    @staticmethod
    def str_list(name: str, value: t.Any) -> list[str]:
        if is_list_of(value, str):
            return value
        raise validators.ValidationError(f"'{name}' must be a list of strings")

    @staticmethod
    def opt_str_list(name: str, value: t.Any) -> list[str] | None:
        if is_optional_list_of(value, str):
            return value
        raise validators.ValidationError(f"'{name}' must be a list of strings or null")

    @staticmethod
    def opt_str_list_or_commasep(name: str, value: t.Any) -> list[str] | None:
        if is_optional_list_of(value, str):
            return value
        if isinstance(value, str):
            return value.split(",")
        raise validators.ValidationError(
            f"'{name}' must be a list of strings or a comma-delimited string or null"
        )

    @staticmethod
    def instance_or_dict(name: str, value: t.Any, cls: type[S]) -> S:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls.from_dict(value)
        raise validators.ValidationError(
            f"'{name}' must be a '{cls.__name__}' object or a dictionary"
        )
