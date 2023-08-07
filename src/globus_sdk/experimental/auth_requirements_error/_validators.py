from __future__ import annotations

import typing as t

from ._serializable import Serializable

S = t.TypeVar("S", bound=Serializable)


class ValidationError(ValueError):
    pass


def str_(name: str, value: t.Any) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"'{name}' must be a string")
    return value


def opt_str(name: str, value: t.Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(f"'{name}' must be a string")
    return value


def opt_bool(name: str, value: t.Any) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValidationError(f"'{name}' must be a bool")
    return value


def str_list(name: str, value: t.Any) -> list[str]:
    if not (isinstance(value, list) and all(isinstance(s, str) for s in value)):
        raise ValidationError(f"'{name}' must be a list of strings")
    return value


def opt_str_list(name: str, value: t.Any) -> list[str] | None:
    if value is None:
        return None
    if not (isinstance(value, list) and all(isinstance(s, str) for s in value)):
        raise ValidationError(f"'{name}' must be a list of strings")
    return value


def opt_str_list_or_commasep(name: str, value: t.Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.split(",")
    if not (isinstance(value, list) and all(isinstance(s, str) for s in value)):
        raise ValidationError(f"'{name}' must be a list of strings")
    return value


def instance_or_dict(name: str, value: t.Any, cls: type[S]) -> S:
    if isinstance(value, cls):
        return value
    if isinstance(value, dict):
        return cls.from_dict(value)
    raise ValidationError(f"'{name}' must be a '{cls.__name__}' object or a dictionary")
