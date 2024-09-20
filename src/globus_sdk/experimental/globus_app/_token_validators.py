from __future__ import annotations

import typing as t

import globus_sdk
from globus_sdk.experimental.tokenstorage import TokenStorage, TokenStorageData
from globus_sdk.scopes.consents import ConsentForest

from .errors import (
    IdentityMismatchError,
    MissingIdentityError,
    UnmetScopeRequirementsError,
)


def _get_identity_id_from_token_data_by_resource_server(
    token_data_by_resource_server: t.Mapping[str, TokenStorageData]
) -> str | None:
    """
    Get the identity_id attribute from all TokenStorageData objects by resource server
    Sanity check that they are all the same, and then return that identity_id or None
    """
    token_data_identity_ids: set[str] = set()

    for token_data in token_data_by_resource_server.values():
        if token_data.identity_id:
            token_data_identity_ids.add(token_data.identity_id)

    if len(token_data_identity_ids) == 0:
        return None
    elif len(token_data_identity_ids) == 1:
        return token_data_identity_ids.pop()
    else:
        raise ValueError(
            "token_data_by_resource_server contained TokenStorageData objects with "
            f"different identity_id values: {token_data_identity_ids}"
        )


class UnchangingIdentityIDValidator:
    def __init__(
        self,
        token_storage: TokenStorage,
        *,
        identity_id_callbacks: t.Iterable[t.Callable[[str], None]] = (),
    ) -> None:
        self.identity_id_callbacks: list[t.Callable[[str], None]] = list(
            identity_id_callbacks
        )
        # pull identity_id from the token_storage if possible
        token_data_by_resource_server = (
            token_storage.get_token_data_by_resource_server()
        )

        self._identity_id: str | None = None
        self.identity_id = _get_identity_id_from_token_data_by_resource_server(
            token_data_by_resource_server
        )

    @property
    def identity_id(self) -> str | None:
        return self._identity_id

    @identity_id.setter
    def identity_id(self, value: str) -> None:
        self._identity_id = value
        for callback in self.identity_id_callbacks:
            callback(value)

    def before_store(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        Validate that the identity info in the token data matches the stored identity
        info.

        Side Effect
        ===========
        If no identity info was previously stored, the attached identity is considered
        authoritative and stored on the validator instance.

        :raises: :exc:`IdentityMismatchError` if the identity info in the token data
            does not match the stored identity info.
        :raises :exc:`MissingIdentityError` if the token data did not have identity
            information (generally due to missing the openid scope)
        """
        token_data_identity_id = _get_identity_id_from_token_data_by_resource_server(
            token_data_by_resource_server
        )

        if token_data_identity_id is None:
            raise MissingIdentityError(
                "Token grant response doesn't contain an id_token. This normally "
                "occurs if the auth flow didn't include 'openid' alongside other "
                "scopes."
            )

        if self.identity_id is None:
            self.identity_id = token_data_identity_id
            return

        if token_data_identity_id != self.identity_id:
            raise IdentityMismatchError(
                "Detected a change in identity associated with the token data.",
                stored_id=self.identity_id,
                new_id=token_data_identity_id,
            )


class ConsentRequirementsValidator:
    def __init__(
        self,
        scope_requirements: dict[str, list[globus_sdk.Scope]],
        consent_client: globus_sdk.AuthClient | None = None,
    ) -> None:
        self.consent_client: globus_sdk.AuthClient | None = None
        self.scope_requirements = scope_requirements
        self.identity_id: str | None = None
        self._cached_consent_forest = None

    def set_identity_id(self, value: str) -> None:
        self.identity_id = value

    def before_store(
        self, token_data_by_resource_server: t.Mapping[str, TokenStorageData]
    ) -> None:
        """
        Validate the token data against scope requirements, but do not check
        dependent scopes before storage.
        """
        for resource_server, token_data in token_data_by_resource_server.items():
            self._validate_token_data_meets_scope_requirements(
                resource_server, token_data, eval_dependent=False
            )

    def after_retrieve(self, token_data: TokenStorageData) -> None:
        """
        Validate the token data against scope requirements, including dependent
        scope requirements.
        """
        self._validate_token_data_meets_scope_requirements(
            token_data.resource_server, token_data
        )

    def _poll_and_cache_consents(self) -> ConsentForest | None:
        """
        Poll for consents, caching and returning the result.

        :returns: The consent forest associated with the stored identity, or None if no
            stored identity info is present.
        """
        if self.identity_id is None or self.consent_client is None:
            return None

        forest = self.consent_client.get_consents(self.identity_id).to_forest()
        # Cache the consent forest first.
        self._cached_consent_forest = forest
        return forest

    def _validate_token_data_meets_scope_requirements(
        self,
        resource_server: str,
        token_data: TokenStorageData,
        eval_dependent: bool = True,
    ) -> None:
        """
        Given a particular resource server/token data, evaluate whether the token +
            user's consent forest meet the attached scope requirements.

        Note: If consent_client was omitted, only root scope requirements are validated.

        :param resource_server: The resource server string to validate against.
        :param token_data: The token data to validate against.
        :param eval_dependent: Whether to evaluate dependent scope requirements.
        :raises: :exc:`UnmetScopeRequirements` if token/consent data does not meet the
            attached root or dependent scope requirements for the resource server.
        :returns: None if all scope requirements are met (or indeterminable).
        """
        required_scopes = self.scope_requirements.get(resource_server)

        # Short circuit - No scope requirements are, by definition, met.
        if required_scopes is None:
            return

        # 1. Does the token meet root scope requirements?
        root_scopes = token_data.scope.split(" ")
        if not all(scope.scope_string in root_scopes for scope in required_scopes):
            raise UnmetScopeRequirementsError(
                "Unmet scope requirements",
                scope_requirements=self.scope_requirements,
            )

        # Short circuit - No dependent scopes; don't validate them.
        if not eval_dependent or not any(
            scope.dependencies for scope in required_scopes
        ):
            return

        # 2. Does the consent forest meet all dependent scope requirements?
        # 2a. Try with the cached consent forest first.
        forest = self._cached_consent_forest
        if forest is not None and forest.meets_scope_requirements(required_scopes):
            return

        # 2b. Poll for fresh consents and try again.
        forest = self._poll_and_cache_consents()
        if forest is not None:
            if not forest.meets_scope_requirements(required_scopes):
                raise UnmetScopeRequirementsError(
                    "Unmet dependent scope requirements",
                    scope_requirements=self.scope_requirements,
                )
