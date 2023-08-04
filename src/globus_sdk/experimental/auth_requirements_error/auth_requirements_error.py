from __future__ import annotations

import typing as t

from globus_sdk.exc import GlobusError

from . import validators


class GlobusAuthorizationParameters:
    """
    Represents authorization parameters that can be used to instruct a client
    which additional authorizations are needed in order to complete a request.

    :ivar session_message: A message to be displayed to the user.
    :vartype session_message: str, optional

    :ivar session_required_identities: A list of identities required for the
        session.
    :vartype session_required_identities: list of str, optional

    :ivar session_required_policies: A list of policies required for the
        session.
    :vartype session_required_policies: list of str, optional

    :ivar session_required_single_domain: A list of domains required for the
        session.
    :vartype session_required_single_domain: list of str, optional

    :ivar session_required_mfa: Whether MFA is required for the session.
    :vartype session_required_mfa: bool, optional

    :ivar required_scopes: A list of scopes for which consent is required.
    :vartype required_scopes: list of str, optional

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    session_message: str | None
    session_required_identities: list[str] | None
    session_required_policies: list[str] | None
    session_required_single_domain: list[str] | None
    session_required_mfa: bool | None
    required_scopes: list[str] | None
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "session_message": validators.OptionalString,
        "session_required_identities": validators.OptionalListOfStrings,
        "session_required_policies": validators.OptionalListOfStrings,
        "session_required_single_domain": validators.OptionalListOfStrings,
        "session_required_mfa": validators.OptionalBool,
        "required_scopes": validators.OptionalListOfStrings,
    }

    def __init__(
        self,
        *,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: list[str] | None = None,
        session_required_single_domain: list[str] | None = None,
        session_required_mfa: bool | None = None,
        required_scopes: list[str] | None = None,
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

        # Enforce that the error contains at least one of the fields we expect
        if not any(
            (getattr(self, field_name) is not None)
            for field_name in self.SUPPORTED_FIELDS.keys()
        ):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                + ", ".join(self.SUPPORTED_FIELDS.keys())
            )

    @classmethod
    def from_dict(cls, param_dict: dict[str, t.Any]) -> GlobusAuthorizationParameters:
        """
        Instantiate from an authorization parameters dictionary.

        :param param_dict: The dictionary to create the error from.
        :type param_dict: dict
        """

        # Extract any extra fields
        extras = {k: v for k, v in param_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = param_dict.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Return an authorization parameters dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        :type include_extra: bool
        """
        error_dict = {}

        # Set any authorization parameters
        for field in self.SUPPORTED_FIELDS.keys():
            if getattr(self, field) is not None:
                error_dict[field] = getattr(self, field)

        # Set any extra fields
        if include_extra:
            error_dict.update(self.extra_fields)

        return error_dict


class GlobusAuthRequirementsError(GlobusError):
    """
    Represents a Globus Auth Requirements Error.

    A Globus Auth Requirements Error is a class of error that is returned by Globus
    services to indicate that additional authorization is required in order to complete
    a request and contains information that can be used to request the appropriate
    authorization.

    :ivar code: The error code for this error.
    :vartype code: str

    :ivar authorization_parameters: The authorization parameters for this error.
    :vartype authorization_parameters: GlobusAuthorizationParameters

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    code: str
    authorization_parameters: GlobusAuthorizationParameters
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "code": validators.String,
        "authorization_parameters": validators.ClassInstance(
            GlobusAuthorizationParameters
        ),
    }

    def __init__(
        self,
        code: str | None,  # pylint: disable=unused-argument
        authorization_parameters: dict[str, t.Any]
        | GlobusAuthorizationParameters
        | None,
        *,
        extra: dict[str, t.Any] | None = None,
    ):
        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = GlobusAuthorizationParameters.from_dict(
                param_dict=authorization_parameters
            )

        # Validate and assign supported fields
        for field_name, validator in self.SUPPORTED_FIELDS.items():
            try:
                field_value = validator(locals()[field_name])
            except ValueError as e:
                raise ValueError(f"Error validating field '{field_name}': {e}") from e

            setattr(self, field_name, field_value)

        self.extra_fields = extra or {}

    @classmethod
    def from_dict(cls, error_dict: dict[str, t.Any]) -> GlobusAuthRequirementsError:
        """
        Instantiate a GlobusAuthRequirementsError from a dictionary.

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

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Return a Globus Auth Requirements Error response dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields
            in the dictionary.
        :type include_extra: bool, optional (default: False)
        """
        error_dict = {
            "code": self.code,
            "authorization_parameters": self.authorization_parameters.to_dict(
                include_extra=include_extra
            ),
        }

        # Set any extra fields
        if include_extra:
            error_dict.update(self.extra_fields)

        return error_dict
