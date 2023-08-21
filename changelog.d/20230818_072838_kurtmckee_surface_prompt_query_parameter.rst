Added
~~~~~

-   Add a ``prompt`` keyword parameter to ``AuthClient.oauth2_get_authorize_url()``. (:pr:`813`)

    Setting this parameter requires users to authenticate with an identity provider,
    even if they are already logged in. Doing so can help avoid errors caused by
    unexpected session required policies, which would otherwise require a second,
    follow-up login flow.

    ``prompt`` could previously only be set via the ``query_params`` keyword parameter.
    It is now more discoverable.
