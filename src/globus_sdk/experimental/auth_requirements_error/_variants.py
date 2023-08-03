from __future__ import annotations

import typing as t

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

    @classmethod
    def from_dict(cls: t.Type[T], error_dict: dict[str, t.Any]) -> T:
        raise NotImplementedError()

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
        "code": (str,),
        "required_scopes": (list,),
    }

    def __init__(
        self,
        code: str | None,
        required_scopes: list[str] | None,
        extra: dict[str, t.Any] | None = None,
    ):
        # Needed to make mypy happy w/ stricter types on instance vars.
        # Will clean up in a subsequent commit
        if not isinstance(code, str) or code != "ConsentRequired":
            raise ValueError("'code' must be the string 'ConsentRequired'")

        if not isinstance(required_scopes, list):
            raise ValueError("'required_scopes' must be a list")

        self.code = code
        self.required_scopes = required_scopes
        self.extra_fields = extra or {}

    def to_auth_requirements_error(self) -> GlobusAuthRequirementsError:
        """
        Return a GlobusAuthRequirementsError representing this error.
        """
        return GlobusAuthRequirementsError(
            code=self.code,
            authorization_parameters=GlobusAuthorizationParameters(
                session_required_scopes=self.required_scopes,
                session_message=self.extra_fields.get("message"),
            ),
            extra=self.extra_fields,
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
        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)


class LegacyConsentRequiredAPError(LegacyAuthRequirementsErrorVariant):
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    code: str
    required_scope: str
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "code": (str,),
        "required_scope": (str,),
    }

    def __init__(
        self,
        code: str | None,
        required_scope: str | None,
        extra: dict[str, t.Any] | None,
    ):
        # Needed to make mypy happy w/ stricter types on instance vars.
        # Will clean up in a subsequent commit
        if not isinstance(code, str) or code != "ConsentRequired":
            raise ValueError("'code' must be the string 'ConsentRequired'")

        if not isinstance(required_scope, str):
            raise ValueError("'required_scope' must be a list")

        self.code = code
        self.required_scope = required_scope
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
                session_required_scopes=[self.required_scope],
                session_message=self.extra_fields.get("description"),
                extra=self.extra_fields.get("authorization_parameters"),
            ),
            extra={
                k: v
                for k, v in self.extra_fields.items()
                if k != "authorization_parameters"
            },
        )

    @classmethod
    def from_dict(cls, error_dict: dict[str, t.Any]) -> LegacyConsentRequiredAPError:
        """
        Instantiate from an error dictionary. Raises a ValueError if the dictionary
        does not contain a recognized LegacyConsentRequiredAPError.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """

        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)


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
    session_required_scopes: list[str] | None
    extra_fields: dict[str, t.Any]

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
        extra: dict[str, t.Any] | None = None,
    ):
        self.session_message = session_message
        self.session_required_identities = session_required_identities
        self.session_required_policies = session_required_policies
        self.session_required_single_domain = session_required_single_domain
        self.session_required_mfa = session_required_mfa
        # Declared here for compatibility with mixed legacy payloads
        self.session_required_scopes = session_required_scopes
        # Retain any additional fields
        self.extra_fields = extra or {}

        # Enforce that the error contains at least one of the fields we expect
        if not any(
            (getattr(self, field_name) is not None)
            for field_name in self.SUPPORTED_FIELDS.keys()
        ):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                ", ".join(self.SUPPORTED_FIELDS.keys())
            )

        # Enforce the field types
        for field_name, field_types in self.SUPPORTED_FIELDS.items():
            field_value = getattr(self, field_name)
            if field_value is not None and not isinstance(field_value, field_types):
                raise ValueError(f"'{field_name}' must be one of {field_types}")

    def to_authorization_parameters(
        self,
    ) -> GlobusAuthorizationParameters:
        """
        Return a GlobusAuthRequirementsError representing this error.

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
            session_required_scopes=self.session_required_scopes,
            extra=self.extra_fields,
        )

    @classmethod
    def from_dict(cls, param_dict: dict[str, t.Any]) -> LegacyAuthorizationParameters:
        """
        Create from a dictionary. Raises a ValueError if the dictionary does not contain
        a recognized LegacyAuthorizationParameters format.

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
        "code": (str,),
        "authorization_parameters": (LegacyAuthorizationParameters,),
    }

    def __init__(
        self,
        authorization_parameters: dict[str, t.Any]
        | LegacyAuthorizationParameters
        | None,
        code: str | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.code = code or self.DEFAULT_CODE

        if isinstance(authorization_parameters, LegacyAuthorizationParameters):
            self.authorization_parameters = authorization_parameters
        elif isinstance(authorization_parameters, dict):
            self.authorization_parameters = LegacyAuthorizationParameters.from_dict(
                param_dict=authorization_parameters
            )
        else:
            raise ValueError("Must have 'authorization_parameters'")

        # Retain any additional fields
        self.extra_fields = extra or {}

    @classmethod
    def from_dict(
        cls, error_dict: dict[str, t.Any]
    ) -> LegacyAuthorizationParametersError:
        """
        Instantiate a LegacyAuthorizationParametersError from a dictionary.
        """

        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)

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
