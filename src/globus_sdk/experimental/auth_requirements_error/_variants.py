from __future__ import annotations

import sys
import typing as t

from . import _meta, _validators
from .auth_requirements_error import (
    GlobusAuthorizationParameters,
    GlobusAuthRequirementsError,
)

T = t.TypeVar("T")

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol


class LegacyAuthRequirementsErrorVariant(Protocol):
    """
    Protocol for errors which can be converted to a Globus Auth Requirements Error.
    """

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        ...

    @classmethod
    def from_dict(cls: type[T], data: dict[str, t.Any]) -> T:
        ...

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        ...


class LegacyConsentRequiredTransferError(_meta.ValidatedStruct):
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scopes: t.List[str],
        extra: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.code = code
        self.required_scopes = required_scopes
        self.extra = extra or {}

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


class LegacyConsentRequiredAPError(_meta.ValidatedStruct):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    def __init__(
        self,
        *,
        code: Literal["ConsentRequired"],
        required_scope: str,
        extra: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.code = code
        self.required_scope = required_scope
        self.extra = extra or {}

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


class LegacyAuthorizationParameters(_meta.ValidatedStruct):
    """
    An Authorization Parameters object that describes all known variants in use by
    Globus services.
    """

    _REQUIRE_AT_LEAST_ONE = (
        "supported authorization parameter",
        [
            "session_required_identities",
            "session_required_policies",
            "session_required_single_domain",
            "session_required_mfa",
        ],
    )

    def __init__(
        self,
        *,
        session_message: t.Optional[str] = None,
        session_required_identities: t.Optional[t.List[str]] = None,
        session_required_policies: t.Annotated[
            t.Union[str, t.List[str], None],
            _validators.OptionalListOfStringsOrCommaDelimitedStrings,
        ] = None,
        session_required_single_domain: t.Annotated[
            t.Union[str, t.List[str], None],
            _validators.OptionalListOfStringsOrCommaDelimitedStrings,
        ] = None,
        session_required_mfa: t.Optional[bool] = None,
        extra: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.session_message = session_message
        self.session_required_identities = session_required_identities
        # note the types on these two
        #
        # because the validator returns a list[str] from any input string,
        # the type of the instance variables is narrower than the accepted
        # type for the relevant __init__ parameters
        #
        # because this is done post-__init__ via the metaclass, type checkers
        # are not expected to infer it correctly
        self.session_required_policies: (
            list[str] | None
        ) = session_required_policies  # type: ignore[assignment]
        self.session_required_single_domain: (
            list[str] | None
        ) = session_required_single_domain  # type: ignore[assignment]

        self.session_required_mfa = session_required_mfa
        self.extra = extra or {}

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


class LegacyAuthorizationParametersError(_meta.ValidatedStruct):
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"

    def __init__(
        self,
        *,
        authorization_parameters: t.Annotated[
            t.Union[t.Dict[str, t.Any], LegacyAuthorizationParameters],
            _validators.IsInstance(LegacyAuthorizationParameters),
        ],
        code: t.Annotated[t.Optional[str], _validators.String] = None,
        extra: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        # Apply default, if necessary
        self.code: str = code or self.DEFAULT_CODE
        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = LegacyAuthorizationParameters.from_dict(
                authorization_parameters
            )
        self.authorization_parameters: LegacyAuthorizationParameters = (
            authorization_parameters
        )

        self.extra = extra or {}

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
