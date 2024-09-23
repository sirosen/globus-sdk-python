from __future__ import annotations

import abc
import copy
import typing as t

from globus_sdk import AuthClient, AuthLoginClient, GlobusSDKUsageError, Scope
from globus_sdk._types import ScopeCollectionType, UUIDLike
from globus_sdk.authorizers import GlobusAuthorizer
from globus_sdk.experimental.tokenstorage import TokenStorage
from globus_sdk.gare import GlobusAuthorizationParameters
from globus_sdk.scopes import AuthScopes, scopes_to_scope_list

from ._types import TokenStorageProvider
from ._validating_token_storage import ScopeAndIdentityValidatingTokenStorage
from .authorizer_factory import AuthorizerFactory
from .config import DEFAULT_CONFIG, KNOWN_TOKEN_STORAGES, GlobusAppConfig
from .errors import TokenValidationError


class GlobusApp(metaclass=abc.ABCMeta):
    """
    ``GlobusApp`` is an abstract base class providing an interface for simplifying
    authentication with Globus services.

    A ``GlobusApp`` manages scope requirements across multiple resource servers,
    runs login flows through its ``LoginFlowManager``, handles token storage and
    validation through its ``ValidatingTokenStorage``, and provides up-to-date
    authorizers from its ``AuthorizerFactory`` through ``get_authorizer``.

    A ``GlobusApp`` is accepted as an initialization parameter to any SDK-provided
    service client, automatically handling the client's default scope requirements and
    providing the client with an authorizer.

    :param app_name: A string to identify this app. Used for default tokenstorage
        location and in the future will be used to set user-agent when this app is
        attached to a service client
    :param login_client: An ``AuthLoginCLient`` that will be used for running
        authentication flows. Different classes of ``GlobusApp`` may require
        specific classes of ``AuthLoginClient``. ``Mutually exclusive with
        ``client_id`` and ``client_secret``.
    :param client_id: A client UUID used to construct an ``AuthLoginCLient`` for running
        authentication flows. The type of ``AuthLoginCLient`` will depend on the
        type of ``GlobusApp``. Mutually exclusive with ``login_client``.
    :param client_secret: The value of the client secret for ``client_id`` if it uses
        secrets. Mutually exclusive with ``login_client``.
    :param scope_requirements: A dictionary of scope requirements indexed by
        resource server. The dict value may be a scope, scope string, or list of
        scopes or scope strings.
    :param config: A ``GlobusAppConfig`` used to control various behaviors of this app.

    :ivar token_storage: The ``TokenStorage`` containing tokens for the app and
        capable of validating identity and scope requirements.
        Authorization mediated by the app will use this object, so modifying this will
        impact clients which are defined to use the app whenever they fetch tokens.
    """

    _login_client: AuthLoginClient
    _authorizer_factory: AuthorizerFactory[GlobusAuthorizer]

    def __init__(
        self,
        app_name: str = "Unnamed Globus App",
        *,
        login_client: AuthLoginClient | None = None,
        client_id: UUIDLike | None = None,
        client_secret: str | None = None,
        scope_requirements: t.Mapping[str, ScopeCollectionType] | None = None,
        config: GlobusAppConfig = DEFAULT_CONFIG,
    ) -> None:
        self.app_name = app_name
        self.config = config

        self.client_id, self._login_client = self._resolve_client_info(
            app_name=self.app_name,
            config=self.config,
            client_id=client_id,
            client_secret=client_secret,
            login_client=login_client,
        )
        self._scope_requirements = self._resolve_scope_requirements(scope_requirements)
        self._token_storage = self._resolve_token_storage(
            app_name=self.app_name,
            client_id=self.client_id,
            config=self.config,
        )

        # construct ValidatingTokenStorage around the TokenStorage and
        # our initial scope requirements
        self.token_storage = ScopeAndIdentityValidatingTokenStorage(
            token_storage=self._token_storage,
            scope_requirements=self._scope_requirements,
        )

        # initialize our authorizer factory
        self._initialize_authorizer_factory()

        # create a consent client for token validation
        # reducing the scope requirements to barebones openid (user identification)
        # additionally, this will ensure that openid scope requirement is always
        # registered (it's required for token identity validation).
        consent_client = AuthClient(app=self, app_scopes=[Scope(AuthScopes.openid)])
        self.token_storage.set_consent_client(consent_client)

    def _resolve_scope_requirements(
        self, scope_requirements: t.Mapping[str, ScopeCollectionType] | None
    ) -> dict[str, list[Scope]]:
        if scope_requirements is None:
            return {}

        return {
            resource_server: scopes_to_scope_list(scopes)
            for resource_server, scopes in scope_requirements.items()
        }

    def _resolve_client_info(
        self,
        app_name: str,
        config: GlobusAppConfig,
        login_client: AuthLoginClient | None,
        client_id: UUIDLike | None,
        client_secret: str | None,
    ) -> tuple[UUIDLike, AuthLoginClient]:
        """
        Extracts a client_id and login_client from GlobusApp initialization parameters,
        validating that the parameters were provided correctly.

        Depending on which parameters were provided, this method will either:
            1.  Create a new login client from the supplied credentials.
                *   The actual initialization is performed by the subclass using the
                    abstract method: _initialize_login_client``.
            2.  Extract the client_id from a supplied login_client.

        :returns: tuple of client_id and login_client
        :raises: GlobusSDKUsageError if a single client ID or login client could not be
            definitively resolved.
        """
        if login_client and client_id:
            msg = "Mutually exclusive parameters: client_id and login_client."
            raise GlobusSDKUsageError(msg)

        if login_client:
            # User provided an explicit login client, extract the client_id.
            if login_client.client_id is None:
                msg = "A GlobusApp login_client must have a discoverable client_id."
                raise GlobusSDKUsageError(msg)
            if login_client.environment != config.environment:
                raise GlobusSDKUsageError(
                    "[Environment Mismatch] The login_client's environment "
                    f"({login_client.environment}) does not match the GlobusApp's "
                    f"configured environment ({config.environment})."
                )

            return login_client.client_id, login_client

        elif client_id:
            # User provided an explicit client_id, construct a login client
            login_client = self._initialize_login_client(
                app_name, config, client_id, client_secret
            )
            return client_id, login_client

        else:
            raise GlobusSDKUsageError(
                "Could not set up a globus login client. One of client_id or "
                "login_client is required."
            )

    @abc.abstractmethod
    def _initialize_login_client(
        self,
        app_name: str,
        config: GlobusAppConfig,
        client_id: UUIDLike,
        client_secret: str | None,
    ) -> AuthLoginClient:
        """
        Initializes and returns an AuthLoginClient to be used in authorization requests.
        """

    def _resolve_token_storage(
        self, app_name: str, client_id: UUIDLike, config: GlobusAppConfig
    ) -> TokenStorage:
        """
        Resolve the raw token storage to be used by the app.

        This may be:
            1.  A TokenStorage instance provided by the user, which we use directly.
            2.  A TokenStorageProvider, which we use to get a TokenStorage.
            3.  A string value, which we map onto supported TokenStorage types.

        :returns: TokenStorage instance to be used by the app.
        :raises: GlobusSDKUsageError if the provided token_storage value is unsupported.
        """
        token_storage = config.token_storage
        # TODO - make namespace configurable
        namespace = "DEFAULT"
        if isinstance(token_storage, TokenStorage):
            return token_storage

        elif isinstance(token_storage, TokenStorageProvider):
            return token_storage.for_globus_app(
                app_name=app_name,
                config=config,
                client_id=client_id,
                namespace=namespace,
            )

        elif token_storage in KNOWN_TOKEN_STORAGES:
            provider = KNOWN_TOKEN_STORAGES[token_storage]
            return provider.for_globus_app(
                app_name=app_name,
                config=config,
                client_id=client_id,
                namespace=namespace,
            )

        raise GlobusSDKUsageError(
            f"Unsupported token_storage value: {token_storage}. Must be a "
            f"TokenStorage, TokenStorageProvider, or a supported string value."
        )

    @abc.abstractmethod
    def _initialize_authorizer_factory(self) -> None:
        """
        Initializes self._authorizer_factory to be used for generating authorizers to
        authorize requests.
        """

    def login(
        self,
        *,
        auth_params: GlobusAuthorizationParameters | None = None,
        force: bool = False,
    ) -> None:
        """
        Log an auth entity into the app, if needed, storing the resulting tokens.

        A login flow will be performed if any of the following are true:
            * The kwarg ``auth_params`` is provided.
            * The kwarg ``force`` is set to True.
            * The method ``self.login_required()`` evaluates to True.

        :param auth_params: An optional set of authorization parameters to establish
            requirements and controls for the login flow.
        :param force: If True, perform a login flow even if one does not appear to
            be necessary.
        """
        if auth_params or force or self.login_required():
            self._run_login_flow(auth_params)

    def login_required(self) -> bool:
        """
        Determine if a login flow will be required to interact with resource servers
        under the current scope requirements.

        This will return false if any of the following are true:
            * Access tokens have never been issued.
            * Access tokens have been issued but have insufficient scopes.
            * Access tokens have expired and wouldn't be resolved with refresh tokens.

        :returns: True if a login flow appears to be required, False otherwise.
        """
        for resource_server in self._scope_requirements.keys():
            try:
                self.get_authorizer(resource_server, skip_error_handling=True)
            except TokenValidationError:
                return True
        return False

    def logout(self) -> None:
        """
        Logout an auth entity from the app.

        This will remove and revoke all tokens stored for the current app user.
        """
        # Revoke all tokens, removing them from the underlying token storage
        inner_token_storage = self.token_storage.token_storage
        for resource_server in self._scope_requirements.keys():
            token_data = inner_token_storage.get_token_data(resource_server)
            if token_data:
                self._login_client.oauth2_revoke_token(token_data.access_token)
                if token_data.refresh_token:
                    self._login_client.oauth2_revoke_token(token_data.refresh_token)
                inner_token_storage.remove_token_data(resource_server)

        # Invalidate any cached authorizers
        self._authorizer_factory.clear_cache()

    @abc.abstractmethod
    def _run_login_flow(
        self, auth_params: GlobusAuthorizationParameters | None = None
    ) -> None:
        """
        Run an authorization flow to get new tokens which are stored and available
        for the next authorizer gotten by get_authorizer.

        :param auth_params: An optional set of authorization parameters to establish
            requirements and controls for the login flow.
        """

    def _auth_params_with_required_scopes(
        self,
        auth_params: GlobusAuthorizationParameters | None = None,
    ) -> GlobusAuthorizationParameters:
        """
        Either make a new GlobusAuthorizationParameters with this app's required scopes
        or combine this app's required scopes with given auth_params.
        """
        required_scopes = []
        for scope_list in self._scope_requirements.values():
            required_scopes.extend(scope_list)

        if not auth_params:
            auth_params = GlobusAuthorizationParameters()

        # merge scopes for deduplication to minimize url request length
        # this is useful even if there weren't any auth_param scope requirements
        # as the app's scope_requirements can have duplicates
        combined_scopes = Scope.merge_scopes(
            required_scopes, [Scope(s) for s in auth_params.required_scopes or []]
        )
        auth_params.required_scopes = [str(s) for s in combined_scopes]

        return auth_params

    def get_authorizer(
        self,
        resource_server: str,
        *,
        skip_error_handling: bool = False,
    ) -> GlobusAuthorizer:
        """
        Get a ``GlobusAuthorizer`` from the app's authorizer factory for a specified
        resource server. The type of authorizer is dependent on the app.

        :param resource_server: The resource server for which the requested Authorizer
            should provide authorization headers.
        :param skip_error_handling: If True, skip the configured token validation error
            handler when a ``TokenValidationError`` is raised. Default: False.
        """
        try:
            return self._authorizer_factory.get_authorizer(resource_server)
        except TokenValidationError as e:
            if not skip_error_handling and self.config.token_validation_error_handler:
                # Dispatch to the configured error handler if one is set then retry.
                self.config.token_validation_error_handler(self, e)
                return self._authorizer_factory.get_authorizer(resource_server)
            raise e

    def add_scope_requirements(
        self, scope_requirements: t.Mapping[str, ScopeCollectionType]
    ) -> None:
        """
        Add given scope requirements to the app's scope requirements. Any duplicate
        requirements will be deduplicated later at authorization url creation time.

        :param scope_requirements: a dict of Scopes indexed by resource server
            that will be added to this app's scope requirements
        """
        for resource_server, scopes in scope_requirements.items():
            curr = self._scope_requirements.setdefault(resource_server, [])
            curr.extend(scopes_to_scope_list(scopes))

        self._authorizer_factory.clear_cache(*scope_requirements.keys())

    @property
    def scope_requirements(self) -> dict[str, list[Scope]]:
        """
        Access a copy of app's aggregate scope requirements.

        Modifying the returned dict will not affect the app's scope requirements.
        To add scope requirements, use ``GlobusApp.add_scope_requirements()``.
        """
        # Scopes are mutable objects so we return a deepcopy
        return copy.deepcopy(self._scope_requirements)
