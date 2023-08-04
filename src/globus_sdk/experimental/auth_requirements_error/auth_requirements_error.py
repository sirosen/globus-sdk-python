from __future__ import annotations

import sys
import typing as t

from globus_sdk.exc import GlobusError

from . import validators

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


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

    session_message: Annotated[t.Optional[str], validators.DEFAULT]
    session_required_identities: Annotated[t.Optional[t.List[str]], validators.DEFAULT]
    session_required_policies: Annotated[t.Optional[t.List[str]], validators.DEFAULT]
    session_required_single_domain: Annotated[
        t.Optional[t.List[str]], validators.DEFAULT
    ]
    session_required_mfa: Annotated[t.Optional[bool], validators.DEFAULT]
    required_scopes: Annotated[t.Optional[t.List[str]], validators.DEFAULT]
    extra_fields: t.Dict[str, t.Any]

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
        self.session_message = session_message
        self.session_required_identities = session_required_identities
        self.session_required_policies = session_required_policies
        self.session_required_single_domain = session_required_single_domain
        self.session_required_mfa = session_required_mfa
        self.required_scopes = required_scopes
        self.extra_fields = extra or {}

        validators.run_annotated_validators(self, require_at_least_one=True)

    @classmethod
    def from_dict(cls, param_dict: dict[str, t.Any]) -> GlobusAuthorizationParameters:
        """
        Instantiate from an authorization parameters dictionary.

        :param param_dict: The dictionary to create the error from.
        :type param_dict: dict
        """
        supported_fields = validators.get_supported_fields(cls)

        # Extract any extra fields
        extras = {k: v for k, v in param_dict.items() if k not in supported_fields}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in supported_fields:
            kwargs[field_name] = param_dict.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Return an authorization parameters dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        :type include_extra: bool
        """
        supported_fields = validators.get_supported_fields(self)

        error_dict = {}

        # Set any authorization parameters
        for field in supported_fields:
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

    code: Annotated[str, validators.DEFAULT]
    authorization_parameters: Annotated[
        GlobusAuthorizationParameters,
        validators.ClassInstance(GlobusAuthorizationParameters),
    ]
    extra_fields: t.Dict[str, t.Any]

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

        self.code = code
        self.authorization_parameters = authorization_parameters
        self.extra_fields = extra or {}

        validators.run_annotated_validators(self)

    @classmethod
    def from_dict(cls, error_dict: dict[str, t.Any]) -> GlobusAuthRequirementsError:
        """
        Instantiate a GlobusAuthRequirementsError from a dictionary.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """
        supported_fields = validators.get_supported_fields(cls)

        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in supported_fields}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in supported_fields:
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
