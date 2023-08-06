from __future__ import annotations

import typing as t

from globus_sdk.exc import GlobusError

from . import _validators


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

    :ivar extra: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra: dict
    """

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
    ):
        self.session_message = _validators.OptionalString("session_message")
        self.session_required_identities = _validators.OptionalListOfStrings(
            "session_required_identities"
        )
        self.session_required_policies = _validators.OptionalListOfStrings(
            "session_required_policies"
        )
        self.session_required_single_domain = _validators.OptionalListOfStrings(
            "session_required_single_domain"
        )
        self.session_required_mfa = _validators.OptionalBool("session_required_mfa")
        self.required_scopes = _validators.OptionalListOfStrings("required_scopes")
        self.extra = extra or {}

        _validators.require_at_least_one_field(
            self,
            [f for f in self.SUPPORTED_FIELDS if f != "session_message"],
            "supported authorization parameter",
        )

    SUPPORTED_FIELDS: set[str] = _validators.derive_supported_fields(__init__)

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
        for field_name in cls.SUPPORTED_FIELDS:
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
        for field in self.SUPPORTED_FIELDS:
            if getattr(self, field) is not None:
                error_dict[field] = getattr(self, field)

        # Set any extra fields
        if include_extra:
            error_dict.update(self.extra)

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

    :ivar extra: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra: dict
    """

    _authz_param_validator: _validators.IsInstance[
        GlobusAuthorizationParameters
    ] = _validators.IsInstance(GlobusAuthorizationParameters)

    def __init__(
        self,
        code: str,
        authorization_parameters: dict[str, t.Any] | GlobusAuthorizationParameters,
        *,
        extra: dict[str, t.Any] | None = None,
    ):
        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = GlobusAuthorizationParameters.from_dict(
                param_dict=authorization_parameters
            )

        self.code = _validators.String("code")
        self.authorization_parameters = self._authz_param_validator(
            "authorization_parameters"
        )
        self.extra = extra or {}

    SUPPORTED_FIELDS: set[str] = _validators.derive_supported_fields(__init__)

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
        for field_name in cls.SUPPORTED_FIELDS:
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
            error_dict.update(self.extra)

        return error_dict
