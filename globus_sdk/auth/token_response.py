import logging
import json
import requests
import time

from globus_sdk.response import GlobusHTTPResponse
from globus_sdk.exc import GlobusOptionalDependencyError

logger = logging.getLogger(__name__)


def _convert_token_info_dict(source_dict):
    """
    Extract a set of fields into a new dict for indexing by resource server.
    Allow for these fields to be `None` when absent:
        - "refresh_token"
        - "token_type"
    """
    expires_in = source_dict.get('expires_in', 0)

    return {
        'scope': source_dict['scope'],
        'access_token': source_dict['access_token'],
        'refresh_token': source_dict.get('refresh_token'),
        'token_type': source_dict.get('token_type'),
        'expires_at_seconds': int(time.time() + expires_in)
    }


class OAuthTokenResponse(GlobusHTTPResponse):
    """
    Class for responses from the OAuth2 code for tokens exchange used in
    3-legged OAuth flows.
    """
    def __init__(self, *args, **kwargs):
        GlobusHTTPResponse.__init__(self, *args, **kwargs)

        # call the helper at the top level
        self._by_resource_server = {
            self.resource_server: _convert_token_info_dict(self)}
        # call the helper on everything in 'other_tokens'
        self._by_resource_server.update(dict(
            (unprocessed_item['resource_server'],
             _convert_token_info_dict(unprocessed_item))
            for unprocessed_item in self.other_tokens))

    @property
    def by_resource_server(self):
        """
        Representation of the token response in a ``dict`` indexed by resource
        server.

        Although ``OAuthTokenResponse.data`` is still available and
        valid, this representation is typically more desirable for applications
        doing inspection of access tokens and refresh tokens.
        """
        return self._by_resource_server

    @property
    def expires_at_seconds(self):
        """
        A POSIX timestamp representation of the expiration
        time for the top-level token in the response.
        """
        top_level_token = self._by_resource_server[self.resource_server]
        return top_level_token['expires_at_seconds']

    @property
    def expires_in(self):
        """
        The ``expires_in`` value for the top-level token in the response.
        """
        return int(self.expires_at_seconds - time.time())

    @property
    def access_token(self):
        """
        The ``access_token`` value for the top-level token in the response.
        """
        return self['access_token']

    @property
    def refresh_token(self):
        """
        The ``refresh_token`` value for the top-level token in the response.
        """
        return self.get('refresh_token')

    @property
    def resource_server(self):
        """
        The ``resource_server`` value for the top-level token in the response.
        """
        return self['resource_server']

    @property
    def other_tokens(self):
        """
        The array of tokens other than the top-level one.
        """
        return self['other_tokens']

    def decode_id_token(self, auth_client):
        """
        A parsed ID Token (OIDC) as a dict.
        """
        logger.info('Decoding ID Token "{}"'.format(self['id_token']))
        try:
            from jose import jwt
        except ImportError:
            logger.error('OptionalDependencyError(python-jose)')
            raise GlobusOptionalDependencyError(
                ["python-jose"],
                "JWT Parsing via OAuthTokenResponse.id_token")

        logger.debug('Fetch JWK Data: Start')
        oidc_conf = auth_client.get('/.well-known/openid-configuration')
        jwks_uri = oidc_conf['jwks_uri']
        jwk_data = requests.get(jwks_uri).json()
        logger.debug('Fetch JWK Data: Complete')

        return jwt.decode(
            self['id_token'], jwk_data,
            access_token=self.access_token,
            audience=auth_client.client_id)

    def __str__(self):
        # Make printing responses more convenient by only showing the
        # (typically important) token info
        return json.dumps(self.by_resource_server, indent=2)


class OAuthDependentTokenResponse(GlobusHTTPResponse):
    """
    Class for responses from the OAuth2 code for tokens retrieved by the
    OAuth2 Dependent Token Extension Grant. For more complete docs, see
    :meth:`oauth2_get_dependent_tokens \
    <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
    """
    def __init__(self, *args, **kwargs):
        GlobusHTTPResponse.__init__(self, *args, **kwargs)

        # call the helper on everything in the response array
        self._by_resource_server = dict(
            (unprocessed_item['resource_server'],
             _convert_token_info_dict(unprocessed_item))
            for unprocessed_item in self.data)

    @property
    def by_resource_server(self):
        """
        Representation of the token response in a ``dict`` indexed by resource
        server.

        Although ``OAuthDependentTokenResponse.data`` is still available and
        valid, this representation is typically more desirable for applications
        trying to use the resulting tokens.
        """
        return self._by_resource_server
