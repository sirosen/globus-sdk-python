from __future__ import annotations

import typing as t

from . import _meta, _validators


class GlobusAuthorizationParameters(_meta.ValidatedStruct):
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

    _REQUIRE_AT_LEAST_ONE = (
        "supported authorization parameter",
        [
            "session_required_identities",
            "session_required_policies",
            "session_required_single_domain",
            "session_required_mfa",
            "required_scopes",
        ],
    )

    def __init__(
        self,
        *,
        session_message: t.Optional[str] = None,
        session_required_identities: t.Optional[t.List[str]] = None,
        session_required_policies: t.Optional[t.List[str]] = None,
        session_required_single_domain: t.Optional[t.List[str]] = None,
        session_required_mfa: t.Optional[bool] = None,
        required_scopes: t.Optional[t.List[str]] = None,
        extra: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self.session_message = session_message
        self.session_required_identities = session_required_identities
        self.session_required_policies = session_required_policies
        self.session_required_single_domain = session_required_single_domain
        self.session_required_mfa = session_required_mfa
        self.required_scopes = required_scopes
        self.extra = extra or {}


class GlobusAuthRequirementsError(_meta.ValidatedStruct):
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

    def __init__(
        self,
        code: str,
        authorization_parameters: t.Annotated[
            t.Union[t.Dict[str, t.Any], GlobusAuthorizationParameters],
            _validators.IsInstance(GlobusAuthorizationParameters),
        ],
        *,
        extra: dict[str, t.Any] | None = None,
    ):
        # Convert authorization_parameters if it's a dict
        if isinstance(authorization_parameters, dict):
            authorization_parameters = GlobusAuthorizationParameters.from_dict(
                authorization_parameters
            )

        self.code = code
        self.authorization_parameters = authorization_parameters
        self.extra = extra or {}
