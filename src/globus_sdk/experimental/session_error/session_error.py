import copy
import typing as t

from globus_sdk.exc import GlobusError


class GlobusSessionErrorAuthorizationParameters:
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

    :ivar session_required_scopes: A list of scopes for which consent is required.
    :vartype session_required_scopes: list of str, optional

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    SUPPORTED_FIELDS = {
        "session_message": str,
        "session_required_identities": list,
        "session_required_policies": list,
        "session_required_single_domain": list,
        "session_required_mfa": bool,
        "session_required_scopes": list,
    }

    def __init__(
        self,
        session_message: t.Optional[str] = None,
        session_required_identities: t.Optional[t.List[str]] = None,
        session_required_policies: t.Optional[t.List[str]] = None,
        session_required_single_domain: t.Optional[t.List[str]] = None,
        session_required_mfa: t.Optional[bool] = None,
        session_required_scopes: t.Optional[t.List[str]] = None,
        **kwargs: t.Any,
    ):
        self.session_message: t.Optional[str] = session_message
        self.session_required_identities = session_required_identities
        self.session_required_policies = session_required_policies
        self.session_required_single_domain: t.Optional[
            t.List[str]
        ] = session_required_single_domain
        self.session_required_mfa: t.Optional[bool] = session_required_mfa
        self.session_required_scopes: t.Optional[t.List[str]] = session_required_scopes
        self.extra_fields: t.Dict[str, t.Any] = kwargs

    @classmethod
    def from_dict(
        cls, param_dict: t.Dict[str, t.Any]
    ) -> "GlobusSessionErrorAuthorizationParameters":
        """
        Instantiate from a session error authorization parameters dictionary. Raises
        a ValueError if the dictionary does not contain a valid GlobusSessionError.

        :param param_dict: The dictionary to create the error from.
        :type param_dict: dict
        """

        # Enforce that the error_dict contains at least one of the fields we expect
        if not any(field in param_dict for field in cls.SUPPORTED_FIELDS.keys()):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                ", ".join(cls.SUPPORTED_FIELDS.keys())
            )

        # Enforce the field types
        for field_name, field_type in cls.SUPPORTED_FIELDS.items():
            if field_name in param_dict and not isinstance(
                param_dict[field_name], field_type
            ):
                raise ValueError(
                    f"'{field_name}' must be of type {field_type.__name__}"
                )

        return cls(**param_dict)

    def to_dict(self, include_extra: bool = False) -> t.Dict[str, t.Any]:
        """
        Return a session error authorization parameters dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        :type include_extra: bool
        """
        session_error_dict = {}

        # Set any authorization parameters
        for field in self.SUPPORTED_FIELDS.keys():
            if getattr(self, field) is not None:
                session_error_dict[field] = getattr(self, field)

        # Set any extra fields
        if include_extra:
            session_error_dict.update(self.extra_fields)

        return session_error_dict


class GlobusSessionError(GlobusError):
    """
    Represents a Globus Session Error.

    A Session Error is a class of error that is returned by Globus services to
    indicate that additional authorization is required in order to complete a request
    and contains information that can be used to request the appropriate authorization.

    :ivar code: The error code for this error.
    :vartype code: str

    :ivar authorization_parameters: The authorization parameters for this error.
    :vartype authorization_parameters: GlobusAuthorizationParameters

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    def __init__(
        self,
        code: str,
        authorization_parameters: GlobusSessionErrorAuthorizationParameters,
        **kwargs: t.Any,
    ):
        self.code: str = code
        self.authorization_parameters: GlobusSessionErrorAuthorizationParameters = (
            authorization_parameters
        )
        self.extra_fields = kwargs

    @classmethod
    def from_dict(cls, error_dict: t.Dict[str, t.Any]) -> "GlobusSessionError":
        """
        Instantiate a GlobusSessionError from a dictionary.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """

        if "code" not in error_dict:
            raise ValueError("Must have a 'code'")

        # Enforce that authorization_parameters is in the error_dict and
        # contains at least one of the fields we expect
        if "authorization_parameters" not in error_dict:
            raise ValueError("Must have 'authorization_parameters'")

        kwargs = copy.deepcopy(error_dict)

        # Create our GlobusAuthorizationParameters object
        kwargs[
            "authorization_parameters"
        ] = GlobusSessionErrorAuthorizationParameters.from_dict(
            param_dict=kwargs.pop("authorization_parameters")
        )

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> t.Dict[str, t.Any]:
        """
        Return a session error response dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields
            in the dictionary.
        :type include_extra: bool, optional (default: False)
        """
        session_error_dict = {
            "code": self.code,
            "authorization_parameters": self.authorization_parameters.to_dict(
                include_extra=include_extra
            ),
        }

        # Set any extra fields
        if include_extra:
            session_error_dict.update(self.extra_fields)

        return session_error_dict
