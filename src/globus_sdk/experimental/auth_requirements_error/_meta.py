import functools
import inspect
import sys
import typing as t

from . import _validators

if sys.version_info >= (3, 9):
    from typing import get_type_hints
else:
    from typing_extensions import get_type_hints

V = t.TypeVar("V", bound="ValidatedStruct")


class ValidatedStructMeta(type):
    def __new__(
        cls: type, name: str, bases: tuple[type, ...], namespace: dict[str, t.Any]
    ) -> type:
        # as an escape-valve, skip ValidatedStruct itself
        # this avoids generating these attributes to inherit, and it avoids some
        # awkward requirements (e.g. that all of the helpers have to be defined
        # before ValidatedStruct is defined)
        if name == "ValidatedStruct":
            return super().__new__(  # type: ignore[no-any-return, misc]
                cls, name, bases, namespace
            )
        if "SUPPORTED_FIELDS" not in namespace:
            namespace["SUPPORTED_FIELDS"] = _generate_supported_fields(
                namespace["__init__"]
            )
        validators = namespace.get("_VALIDATORS", {})
        for field_name in namespace["SUPPORTED_FIELDS"]:
            if field_name not in validators:
                validators[field_name] = _derive_validator(field_name, namespace)
        namespace["_VALIDATORS"] = validators
        namespace["__init__"] = _wrap_init(namespace)
        return super().__new__(  # type: ignore[no-any-return, misc]
            cls, name, bases, namespace
        )


class ValidatedStruct(metaclass=ValidatedStructMeta):
    SUPPORTED_FIELDS: t.ClassVar[set[str]]
    _VALIDATORS: dict[str, _validators.Validator[t.Any]]
    extra: dict[str, t.Any]

    @classmethod
    def from_dict(cls: type[V], data: dict[str, t.Any]) -> V:
        """
        Instantiate from a dictionary.

        :param data: The dictionary from which to instantiate.
        :type data: dict
        """
        # Extract any extra fields
        extras = {k: v for k, v in data.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS:
            kwargs[field_name] = data.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Render to a dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        :type include_extra: bool
        """
        result = {}

        # Set any authorization parameters
        for field in self.SUPPORTED_FIELDS:
            value = getattr(self, field)
            if value is not None:
                if isinstance(value, ValidatedStruct):
                    value = value.to_dict(include_extra=include_extra)
                result[field] = value

        # Set any extra fields
        if include_extra:
            result.update(self.extra)

        return result


def _generate_supported_fields(init_callable: t.Callable[..., t.Any]) -> set[str]:
    return set(inspect.signature(init_callable).parameters.keys()) - {"self", "extra"}


def _derive_validator(
    field_name: str, class_namespace: dict[str, t.Any]
) -> _validators.Validator[t.Any]:
    init_method = class_namespace["__init__"]
    field_type = get_type_hints(init_method, include_extras=True)[field_name]
    return _validators.validator_for_type(field_type)


def _wrap_init(namespace: dict[str, t.Any]) -> t.Callable[..., None]:
    init_method: t.Callable[..., None] = namespace["__init__"]

    @functools.wraps(init_method)
    def wrapped_init(self: ValidatedStruct, *args: t.Any, **kwargs: t.Any) -> None:
        init_method(self, *args, **kwargs)
        for field_name, validator in self._VALIDATORS.items():
            value = getattr(self, field_name)
            setattr(self, field_name, validator(field_name, value))
        if "_REQUIRE_AT_LEAST_ONE" in namespace:
            description, requirements = namespace["_REQUIRE_AT_LEAST_ONE"]
            _validators.require_at_least_one_field(self, requirements, description)

    return wrapped_init
