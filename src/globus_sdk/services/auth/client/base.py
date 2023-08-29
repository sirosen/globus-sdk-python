from __future__ import annotations

import json
import logging
import sys
import typing as t

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk import client
from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.scopes import AuthScopes

from ..errors import AuthAPIError

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

log = logging.getLogger(__name__)


class AuthBaseClient(client.BaseClient):
    """
    Common base for all clients for
    `Globus Auth <https://docs.globus.org/api/auth/>`_

    Users should not instantiate this class directly, but should instead use one
    of the provided subclasses.

    .. automethodlist:: globus_sdk.AuthBaseClient
    """

    service_name = "auth"
    error_class = AuthAPIError
    scopes = AuthScopes

    def get_openid_configuration(self) -> GlobusHTTPResponse:
        """
        Fetch the OpenID Connect configuration data from the well-known URI for Globus
        Auth.
        """
        log.info("Fetching OIDC Config")
        return self.get("/.well-known/openid-configuration")

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]),
        *,
        as_pem: Literal[True],
    ) -> RSAPublicKey:
        ...

    @t.overload
    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]),
        *,
        as_pem: Literal[False],
    ) -> dict[str, t.Any]:
        ...

    def get_jwk(
        self,
        openid_configuration: None | (GlobusHTTPResponse | dict[str, t.Any]) = None,
        *,
        as_pem: bool = False,
    ) -> RSAPublicKey | dict[str, t.Any]:
        """
        Fetch the Globus Auth JWK.

        Returns either a dict or an RSA Public Key object depending on ``as_pem``.

        :param openid_configuration: The OIDC config as a GlobusHTTPResponse or dict.
            When not provided, it will be fetched automatically.
        :type openid_configuration: dict or GlobusHTTPResponse
        :param as_pem: Decode the JWK to an RSA PEM key, typically for JWT decoding
        :type as_pem: bool
        """
        log.info("Fetching JWK")
        if openid_configuration:
            jwks_uri = openid_configuration["jwks_uri"]
        else:
            log.debug("No OIDC Config provided, autofetching...")
            jwks_uri = self.get_openid_configuration()["jwks_uri"]

        log.debug("jwks_uri=%s", jwks_uri)
        jwk_data = self.get(jwks_uri).data
        if not as_pem:
            log.debug("returning jwk data where as_pem=False")
            return dict(jwk_data)
        else:
            log.debug("JWK as_pem=True requested, decoding...")
            # decode from JWK to an RSA PEM key for JWT decoding
            # cast here because this should never be private key
            jwk_as_pem: RSAPublicKey = t.cast(
                RSAPublicKey,
                jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk_data["keys"][0])),
            )
            log.debug("JWK PEM decoding finished successfully")
            return jwk_as_pem
