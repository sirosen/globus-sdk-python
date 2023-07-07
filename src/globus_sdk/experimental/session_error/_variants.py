from __future__ import annotations

import typing as t

from .session_error import GlobusSessionError, GlobusSessionErrorAuthorizationParameters

T = t.TypeVar("T", bound="LegacySessionErrorVariant")


class LegacySessionErrorVariant:
    """
    Abstract base class for errors which can be converted to a Globus Session Error.
    """

    @classmethod
    def from_dict(cls: t.Type[T], error_dict: dict[str, t.Any]) -> T:
        raise NotImplementedError()

    def to_session_error(self) -> GlobusSessionError:
        raise NotImplementedError()


class LegacyConsentRequiredTransferError(LegacySessionErrorVariant):
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    def __init__(
        self,
        code: str,
        required_scopes: list[str],
        message: str | None = None,
        request_id: str | None = None,
        resource: str | None = None,
        **kwargs: t.Any,
    ):
        self.code: str = code
        self.required_scopes: list[str] = required_scopes
        self.message: str | None = message
        self.request_id: str | None = request_id
        self.resource: str | None = resource
        self.extra_fields: dict[str, t.Any] = kwargs

    def to_session_error(self) -> GlobusSessionError:
        """
        Return a GlobusSessionError representing this error.
        """
        return GlobusSessionError(
            code=self.code,
            authorization_parameters=GlobusSessionErrorAuthorizationParameters(
                session_required_scopes=self.required_scopes,
                session_message=self.message,
            ),
        )

    @classmethod
    def from_dict(
        cls, error_dict: dict[str, t.Any]
    ) -> LegacyConsentRequiredTransferError:
        """
        Instantiate from an error dictionary. Raises a ValueError if the dictionary
        does not contain a recognized LegacyConsentRequiredTransferError.

        :param error_dict: The dictionary to instantiate the error from.
        :type error_dict: dict
        """
        if error_dict.get("code") != "ConsentRequired":
            raise ValueError("'code' must be 'ConsentRequired'")

        if not error_dict.get("required_scopes"):
            raise ValueError("Must include 'required_scopes'")

        return cls(**error_dict)


class LegacyConsentRequiredAPError(LegacySessionErrorVariant):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    def __init__(
        self,
        code: str,
        required_scope: str,
        description: str | None = None,
        **kwargs: t.Any,
    ):
        self.code: str = code
        self.required_scope: str = required_scope
        self.description: str | None = description
        self.extra_fields: dict[str, t.Any] = kwargs

    def to_session_error(self) -> GlobusSessionError:
        """
        Return a GlobusSessionError representing this error.

        Normalizes the required_scope field to a list and uses the description
        to set the session message.
        """
        return GlobusSessionError(
            code=self.code,
            authorization_parameters=GlobusSessionErrorAuthorizationParameters(
                session_required_scopes=[self.required_scope],
                session_message=self.description,
            ),
        )

    @classmethod
    def from_dict(cls, error_dict: dict[str, t.Any]) -> LegacyConsentRequiredAPError:
        """
        Instantiate from an error dictionary. Raises a ValueError if the dictionary
        does not contain a recognized LegacyConsentRequiredAPError.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """
        if error_dict.get("code") != "ConsentRequired":
            raise ValueError("'code' must be 'ConsentRequired'")

        if not error_dict.get("required_scope"):
            raise ValueError("Must include 'required_scope'")

        return cls(**error_dict)


class LegacyAuthorizationParameters:
    """
    An Authorization Parameters object that describes all known variants in use by
    Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"

    SUPPORTED_FIELDS = {
        "session_message": (str,),
        "session_required_identities": (list,),
        "session_required_policies": (list, str),
        "session_required_single_domain": (list, str),
        "session_required_mfa": (bool,),
        "session_required_scopes": (list,),
    }

    def __init__(
        self,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: str | list[str] | None = None,
        session_required_single_domain: str | list[str] | None = None,
        session_required_mfa: bool | None = None,
        session_required_scopes: list[str] | None = None,
        **kwargs: t.Any,
    ):
        self.session_message: str | None = session_message
        self.session_required_identities: list[str] | None = session_required_identities
        self.session_required_policies: str | list[
            str
        ] | None = session_required_policies
        self.session_required_single_domain: str | list[
            str
        ] | None = session_required_single_domain
        self.session_required_mfa: bool | None = session_required_mfa
        # Declared here for compatibility with mixed legacy payloads
        self.session_required_scopes: list[str] | None = session_required_scopes
        # Retain any additional fields
        self.extra_fields: dict[str, t.Any] = kwargs

    def to_session_error_authorization_parameters(
        self,
    ) -> GlobusSessionErrorAuthorizationParameters:
        """
        Return a GlobusSessionError representing this error.

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

        return GlobusSessionErrorAuthorizationParameters(
            session_message=self.session_message,
            session_required_identities=self.session_required_identities,
            session_required_mfa=self.session_required_mfa,
            session_required_policies=required_policies,
            session_required_single_domain=required_single_domain,
            session_required_scopes=self.session_required_scopes,
            **self.extra_fields,
        )

    @classmethod
    def from_dict(cls, param_dict: dict[str, t.Any]) -> LegacyAuthorizationParameters:
        """
        Create from a dictionary. Raises a ValueError if the dictionary does not contain
        a recognized LegacyAuthorizationParameters format.

        :param param_dict: The dictionary to create the AuthorizationParameters from.
        :type param_dict: dict
        """
        if not any(field in param_dict for field in cls.SUPPORTED_FIELDS.keys()):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                ", ".join(cls.SUPPORTED_FIELDS.keys())
            )

        for field, field_types in cls.SUPPORTED_FIELDS.items():
            if field not in param_dict:
                continue
            if not isinstance(param_dict[field], field_types):
                raise ValueError(
                    f"Field {field} must be one of {field_types}, "
                    "got {error_dict[field]}"
                )

        return cls(**param_dict)


class LegacyAuthorizationParametersError(LegacySessionErrorVariant):
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"

    def __init__(
        self,
        authorization_parameters: LegacyAuthorizationParameters,
        code: str | None = None,
        **kwargs: t.Any,
    ):
        self.authorization_parameters: LegacyAuthorizationParameters = (
            authorization_parameters
        )
        self.code: str = code or self.DEFAULT_CODE
        # Retain any additional fields
        self.extra_fields: dict[str, t.Any] = kwargs

    @classmethod
    def from_dict(
        cls, error_dict: dict[str, t.Any]
    ) -> LegacyAuthorizationParametersError:
        """
        Instantiate a LegacyAuthorizationParametersError from a dictionary.
        """

        # Enforce that authorization_parameters is present in the error_dict
        if not isinstance(error_dict, dict) or not isinstance(
            error_dict.get("authorization_parameters"), dict
        ):
            raise ValueError("Must contain an 'authorization_parameters' dict")

        extra_fields = {
            key: value
            for key, value in error_dict.items()
            if key not in ("authorization_parameters", "code")
        }

        return cls(
            authorization_parameters=LegacyAuthorizationParameters.from_dict(
                error_dict["authorization_parameters"]
            ),
            code=error_dict.get("code"),
            **extra_fields,
        )

    def to_session_error(self) -> GlobusSessionError:
        """
        Return a GlobusSessionError representing this error.
        """
        authorization_parameters = (
            self.authorization_parameters.to_session_error_authorization_parameters()
        )
        return GlobusSessionError(
            authorization_parameters=authorization_parameters,
            code=self.code,
            **self.extra_fields,
        )
