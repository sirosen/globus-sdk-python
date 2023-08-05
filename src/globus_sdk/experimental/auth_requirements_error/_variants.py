from __future__ import annotations

import sys
import typing as t

from . import validators
from .auth_requirements_error import (
    GlobusAuthorizationParameters,
    GlobusAuthRequirementsError,
)

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

T = t.TypeVar("T", bound="LegacyAuthRequirementsErrorVariant")


class HasSupportedFields(Protocol):
    SUPPORTED_FIELDS: t.ClassVar[set[str]]


class LegacyAuthRequirementsErrorVariant(HasSupportedFields):
    """
    Abstract base class for errors which can be converted to a
    Globus Auth Requirements Error.
    """

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
        for field_name in cls.SUPPORTED_FIELDS:
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        raise NotImplementedError()


class LegacyConsentRequiredTransferError(LegacyAuthRequirementsErrorVariant):
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scopes: list[str] | None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.code = _consent_required_validator("code")
        self.required_scopes = validators.ListOfStrings("required_scopes")

        self.extra = extra or {}

    SUPPORTED_FIELDS: set[str] = validators.derive_supported_fields(__init__)

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        return GlobusAuthRequirementsError(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                required_scopes=self.required_scopes,
                session_message=self.extra.get("message"),
            ),
            extra=self.extra,
        )


class LegacyConsentRequiredAPError(LegacyAuthRequirementsErrorVariant):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scope: str,
        extra: dict[str, t.Any] | None,
    ):
        self.code = _consent_required_validator("code")
        self.required_scope = validators.String("required_scope")
        self.extra = extra or {}

    SUPPORTED_FIELDS: set[str] = validators.derive_supported_fields(__init__)

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
                session_message=self.extra.get("description"),
                extra=self.extra.get("authorization_parameters"),
            ),
            extra={
                k: v for k, v in self.extra.items() if k != "authorization_parameters"
            },
        )


class LegacyAuthorizationParameters:
    """
    An Authorization Parameters object that describes all known variants in use by
    Globus services.
    """

    def __init__(
        self,
        *,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: str | list[str] | None = None,
        session_required_single_domain: str | list[str] | None = None,
        session_required_mfa: bool | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.session_message = validators.OptionalString("session_message")
        self.session_required_identities = validators.OptionalListOfStrings(
            "session_required_identities"
        )
        # note the types on these two for clarity; although they should be
        # inferred correctly by most type checkers
        #
        # because the validator returns a list[str] from any input string,
        # the type of the instance variables is narrower than the accepted
        # type for the relevant __init__ parameters
        self.session_required_policies: (
            list[str] | None
        ) = validators.OptionalListOfStringsOrCommaDelimitedStrings(
            "session_required_policies"
        )
        self.session_required_single_domain: (
            list[str] | None
        ) = validators.OptionalListOfStringsOrCommaDelimitedStrings(
            "session_required_single_domain"
        )
        self.session_required_mfa = validators.OptionalBool("session_required_mfa")
        self.extra = extra or {}

        validators.require_at_least_one_field(
            self,
            [f for f in self.SUPPORTED_FIELDS if f != "session_message"],
            "supported authorization parameter",
        )

    SUPPORTED_FIELDS: set[str] = validators.derive_supported_fields(__init__)

    def to_authorization_parameters(self) -> GlobusAuthorizationParameters:
        """
        Return a normalized GlobusAuthorizationParameters instance representing
        these parameters.

        Normalizes fields that may have been provided
        as comma-delimited strings to lists of strings.
        """
        return GlobusAuthorizationParameters(
            session_message=self.session_message,
            session_required_identities=self.session_required_identities,
            session_required_mfa=self.session_required_mfa,
            session_required_policies=self.session_required_policies,
            session_required_single_domain=self.session_required_single_domain,
            extra=self.extra,
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
        for field_name in cls.SUPPORTED_FIELDS:
            kwargs[field_name] = param_dict.get(field_name)

        return cls(**kwargs)


class LegacyAuthorizationParametersError(LegacyAuthRequirementsErrorVariant):
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"
    _authz_param_validator: validators.IsInstance[
        LegacyAuthorizationParameters
    ] = validators.IsInstance(LegacyAuthorizationParameters)

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
        self.code: str = validators.String("code", code or self.DEFAULT_CODE)

        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = LegacyAuthorizationParameters.from_dict(
                param_dict=authorization_parameters
            )
        self.authorization_parameters = self._authz_param_validator(
            "authorization_parameters"
        )
        self.extra = extra or {}

    SUPPORTED_FIELDS: set[str] = validators.derive_supported_fields(__init__)

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
            extra=self.extra,
        )


# construct with an explicit type to get the correct type for the validator
_consent_required_validator: validators.Validator[
    Literal["ConsentRequired"]
] = validators.StringLiteral("ConsentRequired")
