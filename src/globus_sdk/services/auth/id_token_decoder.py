from __future__ import annotations

import abc
import datetime
import typing as t

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

from globus_sdk.response import GlobusHTTPResponse

from ._common import SupportsJWKMethods

if t.TYPE_CHECKING:
    from globus_sdk import AuthLoginClient, GlobusAppConfig


class IDTokenDecoder(abc.ABC):
    """
    This ABC defines a decoder for parsing OIDC id_token data from Globus Auth.
    """

    # default to 300 seconds
    #
    # valuable inputs to this number:
    # - expected clock drift per day (6s for a bad clock)
    # - Windows time sync interval (64s)
    # - Windows' stated goal of meeting the Kerberos 5 clock skew requirement (5m)
    # - ntp panic threshold (1000s of drift)
    # - the knowledge that VM clocks typically run slower and may skew significantly
    #
    # NTP panic should be understood as a critical error; 1000s of drift is
    # therefore too high for us to allow.
    #
    # 300s (5m) is therefore chosen to match the Windows desired maximum for
    # clock drift, and the underlying Kerberos requirement.
    DEFAULT_JWT_LEEWAY: t.ClassVar[float | datetime.timedelta] = 300.0

    def decode(
        self,
        id_token: str,
        *,
        jwt_params: dict[str, t.Any] | None = None,
        leeway: float | datetime.timedelta | None = None,
        audience: str | None = None,
    ) -> dict[str, t.Any]:
        """
        The ``decode()`` method takes an ``id_token`` as a string, and decodes it to
        a dictionary.

        This method should implicitly retrieve the OpenID configuration and JWK
        for Globus Auth.

        :param id_token: The token to decode
        :param jwt_params: An optional dict of parameters to pass to the pyjwt library
            as 'options'
        :param leeway: The leeway to use when verifying JWT expiration times.
        :param audience: The 'audience' to use for JWT verification. Defaults to the
            client ID of the ``auth_client`` provided on init.

        .. note::

            If the client is not an ``AuthLoginClient``, ``audience`` will be required,
            because the ``client_id`` cannot be determined.
        """
        if leeway is None:
            leeway = self.DEFAULT_JWT_LEEWAY

        jwt_audience = audience if audience is not None else self.default_audience
        jwt_params = jwt_params or {}

        openid_configuration = self.get_openid_configuration()
        jwk = self.get_jwk()

        signing_algos = openid_configuration["id_token_signing_alg_values_supported"]

        return jwt.decode(
            id_token,
            key=jwk,
            algorithms=signing_algos,
            audience=jwt_audience,
            options=jwt_params,
            leeway=leeway,
        )

    @property
    def default_audience(self) -> str | None:
        """The default 'audience' for verification of the JWT 'aud' claim."""
        return None

    @abc.abstractmethod
    def get_openid_configuration(self) -> dict[str, t.Any]:
        """Fetch the OpenID Configuration for Globus Auth."""

    @abc.abstractmethod
    def get_jwk(self) -> RSAPublicKey:
        """Fetch the JWK for Globus Auth."""


class DefaultIDTokenDecoder(IDTokenDecoder):
    """
    The default implementation of ID token decoding.

    The default decoder implementation accepts a client on init, and will reach
    out to Globus Auth to fetch OIDC configuration data dynamically, as needed.
    It also has methods to store these values, to avoid the HTTP callouts at time
    of use.

    The main method of a decoder is ``decode()``, which accepts an ``id_token`` string
    and parses it into a dict.

    :param auth_client: The client which should be used to callout to Globus Auth as
        needed. Any AuthClient or AuthLoginClient will work for this purpose.
    """

    def __init__(self, auth_client: SupportsJWKMethods) -> None:
        self._auth_client = auth_client
        self._openid_configuration: dict[str, t.Any] | None = None
        self._jwk: RSAPublicKey | None = None

    @classmethod
    def for_globus_app(
        cls,
        *,
        app_name: str,  # pylint: disable=unused-argument
        config: GlobusAppConfig,  # pylint: disable=unused-argument
        login_client: AuthLoginClient,
    ) -> t.Self:
        """
        Create a ``DefaultIDTokenDecoder`` for use in a GlobusApp.

        :param app_name: The name supplied to the GlobusApp.
        :param config: The configuration supplied to the GlobusApp.
        :param login_client: A login client to use for instantiating an
            ``IDTokenDecoder``.
        """
        return cls(login_client)

    def store_openid_configuration(
        self, openid_configuration: dict[str, t.Any] | GlobusHTTPResponse
    ) -> None:
        """
        Store openid_configuration data for future use in ``decode()``.

        :param openid_configuration: The configuration data, as fetched via
            :meth:`AuthClient.get_openid_configuration`
        """
        if isinstance(openid_configuration, GlobusHTTPResponse):
            self._openid_configuration = openid_configuration.data
        else:
            self._openid_configuration = openid_configuration

    def store_jwk(self, jwk: RSAPublicKey) -> None:
        """
        Store a JWK for future use in ``decode()``.

        :param jwk: The JWK, as fetched via :meth:`AuthClient.get_jwk`
            with ``as_pem=True``.
        """
        self._jwk = jwk

    @property
    def default_audience(self) -> str | None:
        """
        The audience for JWT verification defaults to the client's client ID.
        """
        return self._auth_client.client_id

    def get_openid_configuration(self) -> dict[str, t.Any]:
        """
        Fetch the OpenID Configuration for Globus Auth, and cache the result before
        returning it.

        If a config was previously stored, return that instead.
        """
        if self._openid_configuration is None:
            self._openid_configuration = (
                self._auth_client.get_openid_configuration().data
            )
        return self._openid_configuration

    def get_jwk(self) -> RSAPublicKey:
        """
        Fetch the JWK for Globus Auth, and cache the result before returning it.

        If a key was previously stored, return that instead.
        """
        if not self._jwk:
            self._jwk = self._auth_client.get_jwk(
                openid_configuration=self.get_openid_configuration(), as_pem=True
            )
        return self._jwk
