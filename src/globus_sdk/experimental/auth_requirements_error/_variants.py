from __future__ import annotations

import typing as t

from . import validators
from .auth_requirements_error import (
    GlobusAuthorizationParameters,
    GlobusAuthRequirementsError,
)

T = t.TypeVar("T", bound="LegacyAuthRequirementsErrorVariant")


class LegacyAuthRequirementsErrorVariant:
    """
    Abstract base class for errors which can be converted to a
    Globus Auth Requirements Error.
    """

    SUPPORTED_FIELDS: dict[str, t.Callable[[t.Any], t.Any]] = {}

    @classmethod
    def from_dict(cls: t.Type[T], error_dict: dict[str, t.Any]) -> T:
        """
        Instantiate from an error dictionary.

        :param error_dict: The dictionary to instantiate the error from.
        :type error_dict: dict
        """
        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        raise NotImplementedError()


class LegacyConsentRequiredTransferError(LegacyAuthRequirementsErrorVariant):
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    code: str
    required_scopes: list[str]
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "code": validators.StringLiteral("ConsentRequired"),
        "required_scopes": validators.ListOfStrings,
    }

    def __init__(
        self,
        *,
        code: str | None,
        required_scopes: list[str] | None,
        extra: dict[str, t.Any] | None = None,
    ):  # pylint: disable=unused-argument
        # Validate and assign supported fields
        for field_name, validator in self.SUPPORTED_FIELDS.items():
            try:
                field_value = validator(locals()[field_name])
            except ValueError as e:
                raise ValueError(f"Error validating field '{field_name}': {e}") from e

            setattr(self, field_name, field_value)

        self.extra_fields = extra or {}

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        return GlobusAuthRequirementsError(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                required_scopes=self.required_scopes,
                session_message=self.extra_fields.get("message"),
            ),
            extra=self.extra_fields,
        )


class LegacyConsentRequiredAPError(LegacyAuthRequirementsErrorVariant):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    code: str
    required_scope: str
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "code": validators.StringLiteral("ConsentRequired"),
        "required_scope": validators.String,
    }

    def __init__(
        self,
        *,
        code: str | None,
        required_scope: str | None,
        extra: dict[str, t.Any] | None,
    ):  # pylint: disable=unused-argument
        # Validate and assign supported fields
        for field_name, validator in self.SUPPORTED_FIELDS.items():
            try:
                field_value = validator(locals()[field_name])
            except ValueError as e:
                raise ValueError(f"Error validating field '{field_name}': {e}") from e

            setattr(self, field_name, field_value)

        self.extra_fields = extra or {}

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        """
        Return a GlobusAuthRequirementsError representing this error.

        Normalizes the required_scope field to a list and uses the description
        to set the session message.
        """
        return GlobusAuthRequirementsError(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                required_scopes=[self.required_scope],
                session_message=self.extra_fields.get("description"),
                extra=self.extra_fields.get("authorization_parameters"),
            ),
            extra={
                k: v
                for k, v in self.extra_fields.items()
                if k != "authorization_parameters"
            },
        )


class LegacyAuthorizationParameters:
    """
    An Authorization Parameters object that describes all known variants in use by
    Globus services.
    """

    session_message: str | None
    session_required_identities: list[str] | None
    session_required_policies: str | list[str] | None
    session_required_single_domain: str | list[str] | None
    session_required_mfa: bool | None
    # Declared here for compatibility with mixed legacy payloads
    required_scopes: list[str] | None
    extra_fields: dict[str, t.Any]

    DEFAULT_CODE = "AuthorizationRequired"

    SUPPORTED_FIELDS = {
        "session_message": validators.OptionalString,
        "session_required_identities": validators.OptionalListOfStrings,
        "session_required_policies": (
            validators.OptionalListOfStringsOrCommaDelimitedStrings
        ),
        "session_required_single_domain": (
            validators.OptionalListOfStringsOrCommaDelimitedStrings
        ),
        "session_required_mfa": validators.OptionalBool,
    }

    def __init__(
        self,
        *,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: str | list[str] | None = None,
        session_required_single_domain: str | list[str] | None = None,
        session_required_mfa: bool | None = None,
        extra: dict[str, t.Any] | None = None,
    ):  # pylint: disable=unused-argument
        # Validate and assign supported fields
        for field_name, validator in self.SUPPORTED_FIELDS.items():
            try:
                field_value = validator(locals()[field_name])
            except ValueError as e:
                raise ValueError(f"Error validating field '{field_name}': {e}") from e

            setattr(self, field_name, field_value)

        # Retain any additional fields
        self.extra_fields = extra or {}

        # Enforce that the error contains at least one of the fields we expect
        if all(
            getattr(self, field_name) is None
            for field_name in self.SUPPORTED_FIELDS
        ):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                ", ".join(self.SUPPORTED_FIELDS.keys())
            )

    def to_authorization_parameters(
        self,
    ) -> GlobusAuthorizationParameters:
        """
        Return a normalized GlobusAuthorizationParameters instance representing
        these parameters.

        Normalizes fields that may have been provided
        as comma-delimited strings to lists of strings.
        """
        required_policies = self.session_required_policies
        if isinstance(required_policies, str):
            required_policies = required_policies.split(",")

        # TODO: Unnecessary?
        required_single_domain = self.session_required_single_domain
        if isinstance(required_single_domain, str):
            required_single_domain = required_single_domain.split(",")

        return GlobusAuthorizationParameters(
            session_message=self.session_message,
            session_required_identities=self.session_required_identities,
            session_required_mfa=self.session_required_mfa,
            session_required_policies=required_policies,
            session_required_single_domain=required_single_domain,
            extra=self.extra_fields,
        )

    @classmethod
    def from_dict(cls, param_dict: dict[str, t.Any]) -> LegacyAuthorizationParameters:
        """
        Instantiate from an authorization_parameters dictionary.

        :param param_dict: The dictionary to create the AuthorizationParameters from.
        :type param_dict: dict
        """

        # Extract any extra fields
        extras = {k: v for k, v in param_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = param_dict.get(field_name)

        return cls(**kwargs)


class LegacyAuthorizationParametersError(LegacyAuthRequirementsErrorVariant):
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    authorization_parameters: LegacyAuthorizationParameters
    code: str
    extra_fields: dict[str, t.Any]

    DEFAULT_CODE = "AuthorizationRequired"

    SUPPORTED_FIELDS = {
        "code": validators.String,
        "authorization_parameters": validators.ClassInstance(
            LegacyAuthorizationParameters
        ),
    }

    def __init__(
        self,
        *,
        authorization_parameters: dict[str, t.Any]
        | LegacyAuthorizationParameters
        | None,
        code: str | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        # Apply default, if necessary
        code = code or self.DEFAULT_CODE

        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = LegacyAuthorizationParameters.from_dict(
                param_dict=authorization_parameters
            )

        # Validate and assign supported fields
        for field_name, validator in self.SUPPORTED_FIELDS.items():
            try:
                field_value = validator(locals()[field_name])
            except ValueError as e:
                raise ValueError(f"Error validating field '{field_name}': {e}") from e

            setattr(self, field_name, field_value)

        # Retain any additional fields
        self.extra_fields = extra or {}

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        authorization_parameters = (
            self.authorization_parameters.to_authorization_parameters()
        )
        return GlobusAuthRequirementsError(
            authorization_parameters=authorization_parameters,
            code=self.code,
            extra=self.extra_fields,
        )
