from __future__ import print_function

from globus_sdk import config
from globus_sdk.base import BaseClient
from globus_sdk.authorizers import AccessTokenAuthorizer
from globus_sdk.auth.token_response import OAuthTokenResponse


class AuthClient(BaseClient):
    """
    Client for the
    `Globus Auth API <https://docs.globus.org/api/auth/>`_

    This class provides helper methods for most common resources in the
    Auth API, and the common low-level interface from
    :class:`BaseClient <globus_sdk.base.BaseClient>` of ``get``, ``put``,
    ``post``, and ``delete`` methods, which can be used to access any API
    resource.

    There are generally two types of resources, distinguished by the type
    of authentication which they use. Resources available to end users of
    Globus are authenticated with a Globus Auth Token
    ("Authentication: Bearer ..."), while resources available to OAuth
    Clients are authenticated using Basic Auth with the Client's ID and
    Secret.
    Some resources may be available with either authentication type.

    Initializing an ``AuthClient`` to authenticate a user making calls to the
    Globus Auth service with an access token takes the form

    >>> from globus_sdk import AuthClient
    >>> # AccessTokenAuthorizer is used, loading from the auth_token value in
    >>> # your configuration
    >>> ac = AuthClient()

    or explicitly as

    >>> from globus_sdk import AuthClient, AccessTokenAuthorizer
    >>> ac = AuthClient(authorizer=AccessTokenAuthorizer('<token_string>'))
    """
    def __init__(self, environment=config.get_default_environ(),
                 client_id=None, authorizer=None, app_name=None):
        self.client_id = client_id

        # an AuthClient may contain a GlobusOAuth2FlowManager in order to
        # encapsulate the functionality of various different types of flow
        # managers
        self.current_oauth2_flow_manager = None

        access_token = config.get_auth_token(environment)
        if authorizer is None and access_token is not None:
            authorizer = AccessTokenAuthorizer(access_token)

        BaseClient.__init__(self, "auth", environment, authorizer=authorizer,
                            app_name=app_name)

    def get_identities(self, **params):
        r"""
        GET /v2/api/identities

        Given ``usernames=<U>`` or (exclusive) ``ids=<I>`` as keyword
        arguments, looks up identity information for the set of identities
        provided.
        ``<U>`` and ``<I>`` in this case are comma-delimited strings listing
        multiple Identity Usernames or Identity IDs.

        Available with any authentication/client type.

        >>> ac = globus_sdk.AuthClient()
        >>> # by IDs
        >>> r = ac.get_identities(ids="46bd0f56-e24f-11e5-a510-131bef46955c")
        >>> r.data
        {u'identities': [{u'email': None,
           u'id': u'46bd0f56-e24f-11e5-a510-131bef46955c',
           u'identity_provider': u'7daddf46-70c5-45ee-9f0f-7244fe7c8707',
           u'name': None,
           u'organization': None,
           u'status': u'unused',
           u'username': u'globus@globus.org'}]}
        >>> ac.get_identities(
        >>>     identities=",".join(
        >>>         ("46bd0f56-e24f-11e5-a510-131bef46955c",
        >>>          "168edc3d-c6ba-478c-9cf8-541ff5ebdc1c"))
        ...
        >>> # or by usernames
        >>> ac.get_identities(usernames='globus@globus.org')
        ...
        >>> ac.get_identities(
        >>>     usernames='globus@globus.org,auth@globus.org')
        ...

        See
        `Identities Resources \
        <https://docs.globus.org/api/auth/reference/
        #v2_api_identities_resources>`_
        in the API documentation for details.
        """
        return self.get("/v2/api/identities", params=params)

    def oauth2_get_authorize_url(self, additional_params=None):
        """
        Get the authorization URL to which users should be sent.
        This method may only be called after an ``oauth2_start_flow_*`` method
        has been called on this ``AuthClient``.

        **Parameters**

            ``additional_params`` (*dict*)
              A ``dict`` or ``None``, which specifies additional query
              parameters to include in the authorize URL. Primarily for
              internal use

        :rtype: ``string``
        """
        if not self.current_oauth2_flow_manager:
            raise ValueError(
                ('Cannot get authorize URL until starting an OAuth2 flow. '
                 'Call one of the oauth2_start_flow_*() methods on this '
                 'AuthClient to resolve'))
        return self.current_oauth2_flow_manager.get_authorize_url(
            additional_params=additional_params)

    def oauth2_exchange_code_for_tokens(self, auth_code):
        """
        Exchange an authorization code for a token or tokens.

        :rtype: :class:`OAuthTokenResponse \
        <globus_sdk.auth.token_response.OAuthTokenResponse>`

        ``auth_code``
          An auth code typically obtained by sending the user to the authorize
          URL. The code is a very short-lived credential which this method is
          exchanging for tokens. Tokens are the credentials used to
          authenticate against Globus APIs.
        """
        if not self.current_oauth2_flow_manager:
            raise ValueError(
                ('Cannot exchange auth code until starting an OAuth2 flow. '
                 'Call one of the oauth2_start_flow_*() methods on this '
                 'AuthClient to resolve'))

        return self.current_oauth2_flow_manager.exchange_code_for_tokens(
            auth_code)

    def oauth2_refresh_token(self, refresh_token):
        r"""
        Exchange a refresh token for a :class:`OAuthTokenResponse
        <globus_sdk.auth.token_response.OAuthTokenResponse>`, containing
        an access token.

        Does a token call of the form

        .. code-block:: none

            refresh_token=<refresh_token>
            grant_type=refresh_token

        plus any additional parameters you may specify.

        ``refresh_token``
          A raw Refresh Token string

        ``additional_params``
          A dict of extra params to encode in the refresh call.
        """
        form_data = {'refresh_token': refresh_token,
                     'grant_type': 'refresh_token'}

        return self.oauth2_token(form_data)

    def oauth2_revoke_token(self, token, additional_params=None):
        """
        Revoke a token. It can be an Access Token or a Refresh token.

        Regardless of whether or not your client was issued the token, or of
        any other unusual conditions, this call should always succeed and
        revoke the token so long as the server can understand the request.
        That is, it is best to try to make well-formed calls to this method,
        but it is possible for malformed calls to still result in revocation.

        You can check the "active" status of the token after revocation if you
        want to confirm that it was revoked.

        **Parameters**

            ``token`` (*string*)
              The token which should be revoked

            ``additional_params`` (*dict*)
              A ``dict`` or ``None``, which specifies additional
              parameters to include in the revocation body, which can help
              speed the revocation process. Primarily for internal use

        **Examples**

        Because this call can work even when you have the wrong credentials, it
        can even be called with no credentials at all:

        >>> from globus_sdk import AuthClient
        >>> ac = AuthClient()
        >>> ac.oauth2_revoke_token('<token_string>')

        Or you could do it with a credentialed client type as well:

        >>> from globus_sdk import ConfidentialAppAuthClient
        >>> ac = ConfidentialAppAuthClient(CLIENT_ID, CLIENT_SECRET)
        >>> ac.oauth2_revoke_token('<token_string>')
        """
        body = {'token': token}
        if additional_params:
            body.update(additional_params)
        return self.post('/v2/oauth2/token/revoke', text_body=body)

    def oauth2_token(self, form_data, response_class=OAuthTokenResponse):
        """
        This is the generic form of calling the OAuth2 Token endpoint.
        It takes ``form_data``, a dict which will be encoded in a form POST
        body on the request.

        Generally, users of the SDK should not call this method unless they are
        implementing OAuth2 flows.

        **Parameters**

            ``response_type``
              Defaults to :class:`OAuthTokenResponse \
              <globus_sdk.auth.token_response.OAuthTokenResponse>`. This is
              used by calls to the oauth2_token endpoint which need to
              specialize their responses. For example,
              :meth:`oauth2_get_dependent_tokens \
              <globus_sdk.ConfidentialAppAuthClient.oauth2_get_dependent_tokens>`
              requires a specialize response class to handle the dramatically
              different nature of the Dependent Token Grant response

        :rtype: ``response_class``
        """
        # use the fact that requests implicitly encodes the `data` parameter as
        # a form POST
        return self.post(
            '/v2/oauth2/token', response_class=response_class,
            text_body=form_data)
