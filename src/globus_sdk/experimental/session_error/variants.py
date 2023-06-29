import typing as t

from .session_error import GlobusSessionError, GlobusSessionErrorAuthorizationParameters


class LegacyConsentRequiredTransferError:
    """
    The ConsentRequired error format emitted by the Globus Transfer service.
    """

    def __init__(
        self,
        code: t.Literal["ConsentRequired"],
        required_scopes: t.List[str],
        message: t.Optional[str] = None,
        request_id: t.Optional[str] = None,
        resource: t.Optional[str] = None,
        **kwargs: t.Any,
    ):
        self.code: t.Literal["ConsentRequired"] = code
        self.required_scopes: t.List[str] = required_scopes
        self.message: t.Optional[str] = message
        self.request_id: t.Optional[str] = request_id
        self.resource: t.Optional[str] = resource
        self.extra_fields: t.Dict[str, t.Any] = kwargs

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
        cls, error_dict: t.Dict[str, t.Any]
    ) -> "LegacyConsentRequiredTransferError":
        """
        Instantiate from an error dictionary. Raises a ValueError if the dictionary
        does not contain a recognized LegacyConsentRequiredTransferError.

        :param error_dict: The dictionary to instantiate the error from.
        :type error_dict: dict
        """
        if error_dict.get("code") != "ConsentRequired":
            raise ValueError("Must be a ConsentRequired error")

        if not error_dict.get("required_scopes"):
            raise ValueError("Must include required_scopes")

        return cls(**error_dict)


class LegacyConsentRequiredAPError:
    """
    The ConsentRequired error format emitted by the legacy Globus Transfer
    Action Providers.
    """

    def __init__(
        self,
        code: t.Literal["ConsentRequired"],
        required_scope: str,
        description: t.Optional[str] = None,
        **kwargs: t.Any,
    ):
        self.code: t.Literal["ConsentRequired"] = code
        self.required_scope: str = required_scope
        self.description: t.Optional[str] = description
        self.extra_fields: t.Dict[str, t.Any] = kwargs

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
    def from_dict(
        cls, error_dict: t.Dict[str, t.Any]
    ) -> "LegacyConsentRequiredAPError":
        """
        Instantiate from an error dictionary. Raises a ValueError if the dictionary
        does not contain a recognized LegacyConsentRequiredAPError.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """
        if error_dict.get("code") != "ConsentRequired":
            raise ValueError("Must be a ConsentRequired error")

        if not error_dict.get("required_scope"):
            raise ValueError("Must include required_scope")

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
        session_message: t.Optional[str] = None,
        session_required_identities: t.Optional[t.List[str]] = None,
        session_required_policies: t.Optional[t.Union[str, t.List[str]]] = None,
        session_required_single_domain: t.Optional[t.Union[str, t.List[str]]] = None,
        session_required_mfa: t.Optional[bool] = None,
        session_required_scopes: t.Optional[t.List[str]] = None,
        **kwargs: t.Any,
    ):
        self.session_message: t.Optional[str] = session_message
        self.session_required_identities: t.Optional[
            t.List[str]
        ] = session_required_identities
        self.session_required_policies: t.Optional[
            t.Union[str, t.List[str]]
        ] = session_required_policies
        self.session_required_single_domain: t.Optional[
            t.Union[str, t.List[str]]
        ] = session_required_single_domain
        self.session_required_mfa: t.Optional[bool] = session_required_mfa
        # Declared here for compatibility with mixed legacy payloads
        self.session_required_scopes: t.Optional[t.List[str]] = session_required_scopes
        # Retain any additional fields
        self.extra_fields: t.Dict[str, t.Any] = kwargs

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
    def from_dict(
        cls, param_dict: t.Dict[str, t.Any]
    ) -> "LegacyAuthorizationParameters":
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


class LegacyAuthorizationParametersError:
    """
    Defines an Authorization Parameters error that describes all known variants
    in use by Globus services.
    """

    DEFAULT_CODE = "AuthorizationRequired"

    def __init__(
        self,
        authorization_parameters: LegacyAuthorizationParameters,
        code: t.Optional[str] = None,
        **kwargs: t.Any,
    ):
        self.authorization_parameters: LegacyAuthorizationParameters = (
            authorization_parameters
        )
        self.code: str = code or self.DEFAULT_CODE
        # Retain any additional fields
        self.extra_fields: t.Dict[str, t.Any] = kwargs

    @classmethod
    def from_dict(
        cls, error_dict: t.Dict[str, t.Any]
    ) -> "LegacyAuthorizationParametersError":
        """
        Instantiate a LegacyAuthorizationParametersError from a dictionary.
        """

        # Enforce that authorization_parameters is present in the error_dict
        if not isinstance(error_dict, dict) or not isinstance(
            error_dict.get("authorization_parameters"), dict
        ):
            raise ValueError(
                "LegacyAuthorizationParametersError must be a dict that contains an "
                "'authorization_parameters' dict"
            )

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
