from __future__ import annotations

import typing as t

import globus_sdk
from globus_sdk.experimental.tokenstorage import TokenStorage, TokenStorageData

from ._token_validators import (
    ConsentRequirementsValidator,
    UnchangingIdentityIDValidator,
)
from .errors import MissingTokenError

# before_store validators take token_data_by_resource_server
# and may have any return type
BeforeStoreValidatorT = t.Callable[[t.Mapping[str, TokenStorageData]], t.Any]
# after_retreive validators take token_data
# and may have any return type
AfterRetrieveValidatorT = t.Callable[[TokenStorageData], t.Any]


class ValidatingTokenStorage(TokenStorage):
    """
    A ValidatingTokenStorage wraps another TokenStorage and applies validators when
    storing and retrieving tokens.

    ValidatingTokenStorage is not concerned with the actual storage location of tokens
    but rather validating that they meet requirements.

    :param token_storage: The token storage being wrapped.
    :param before_store_validators: An iterable of validators to use before storing
        token data. These take the full ``{resource_server: token_data}`` mapping and
        raise errors if validation fails.
    :param after_retrieve_validators: An iterable of validators to use after retrieving
        token data. These take the individual ``token_data`` may raise errors if
        validation fails.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        *,
        before_store_validators: t.Iterable[BeforeStoreValidatorT] = (),
        after_retrieve_validators: t.Iterable[AfterRetrieveValidatorT] = (),
    ) -> None:
        self.token_storage = token_storage
        self.before_store_validators: list[BeforeStoreValidatorT] = list(
            before_store_validators
        )
        self.after_retrieve_validators: list[AfterRetrieveValidatorT] = list(
            after_retrieve_validators
        )

        self._identity_id_validator = UnchangingIdentityIDValidator(token_storage)
        self.before_store_validators.append(self._identity_id_validator.before_store)

        super().__init__(namespace=token_storage.namespace)

    def store_token_data_by_resource_server(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        :param token_data_by_resource_server: A dict of TokenStorageData objects
            indexed by their resource server
        """
        for validator in self.before_store_validators:
            validator(token_data_by_resource_server)

        self.token_storage.store_token_data_by_resource_server(
            token_data_by_resource_server
        )

    def get_token_data(self, resource_server: str) -> TokenStorageData:
        """
        :param resource_server: A resource server with cached token data.
        :returns: The token data for the given resource server.
        :raises: :exc:`MissingTokenError` if the underlying ``TokenStorage`` does not
            have any token data for the given resource server.
        """
        token_data = self.token_storage.get_token_data(resource_server)
        if token_data is None:
            msg = f"No token data for {resource_server}"
            raise MissingTokenError(msg, resource_server=resource_server)

        for validator in self.after_retrieve_validators:
            validator(token_data)

        return token_data

    def get_token_data_by_resource_server(self) -> dict[str, TokenStorageData]:
        all_data = self.token_storage.get_token_data_by_resource_server()
        for token_data in all_data.values():
            for validator in self.after_retrieve_validators:
                validator(token_data)
        return all_data

    def remove_token_data(self, resource_server: str) -> bool:
        """
        :param resource_server: The resource server string to remove token data for
        """
        return self.token_storage.remove_token_data(resource_server)


class ScopeAndIdentityValidatingTokenStorage(ValidatingTokenStorage):
    """
    A ValidatingTokenStorage which populates its validators with behaviors for
    validating scopes and identity IDs.

    It also adds behavior for handling identity IDs on refresh tokens more gracefully.
    """

    def __init__(
        self,
        token_storage: TokenStorage,
        *,
        scope_requirements: dict[str, list[globus_sdk.Scope]],
        consent_client: globus_sdk.AuthClient | None = None,
        before_store_validators: t.Iterable[BeforeStoreValidatorT] = (),
        after_retrieve_validators: t.Iterable[AfterRetrieveValidatorT] = (),
    ) -> None:
        super().__init__(
            token_storage,
            before_store_validators=before_store_validators,
            after_retrieve_validators=after_retrieve_validators,
        )
        self._identity_id: str | None = None

        self._consent_validator = ConsentRequirementsValidator(
            scope_requirements, consent_client
        )
        self._identity_id_validator = UnchangingIdentityIDValidator(
            token_storage,
            identity_id_callbacks=(
                self._set_identity_id,
                self._consent_validator.set_identity_id,
            ),
        )
        self.before_store_validators.extend(
            [
                self._identity_id_validator.before_store,
                self._consent_validator.before_store,
            ]
        )
        self.after_retrieve_validators.append(self._consent_validator.after_retrieve)

    def _set_identity_id(self, value: str) -> None:
        self._identity_id = value

    def _extract_identity_id(
        self, token_response: globus_sdk.OAuthTokenResponse
    ) -> str | None:
        """
        Override determination of the identity_id for a token response.

        When handling a refresh token, use the stored identity ID if possible.
        Otherwise, call the inner token storage's method of lookup.
        """
        if isinstance(token_response, globus_sdk.OAuthRefreshTokenResponse):
            return self._identity_id
        else:
            return self.token_storage._extract_identity_id(token_response)

    def set_consent_client(self, consent_client: globus_sdk.AuthClient) -> None:
        """
        Set the consent client to be used for consent polling.

        :param consent_client: An AuthClient to be used for consent polling.
        """
        self._consent_validator.consent_client = consent_client
