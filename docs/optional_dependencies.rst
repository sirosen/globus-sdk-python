.. _optional_dependencies:

Optional Dependencies
=====================

In order to maintain portability while supporting a robust feature set, certain
features of the Globus SDK rely upon optional dependencies.
These dependencies are python packages which are *not* required by the SDK, but
*are* required by specific features.
If you attempt to use such a feature without installing the relevant
dependency, you will get a ``GlobusOptionalDependencyError``.

Optional dependencies are also made available via these extras, specified as
part of your dependency on the ``globus_sdk`` package:

- ``globus_sdk[jwt]``


If you need to specify a version of ``globus_sdk`` while installing the ``jwt``
extra, simply specify it like so: ``globus_sdk[jwt]==1.0.0``


OIDC ID Tokens
--------------

The :class:`OAuthTokenResponse
<globus_sdk.auth.token_response.OAuthTokenResponse>` may include an ID token
conforming to the Open ID Connect specification.
If you wish to decode this token via :meth:`decode_id_token
<globus_sdk.auth.token_response.OAuthTokenResponse.decode_id_token>`, you must
install ``globus_sdk[jwt]``. This extra target includes dependencies which we
use to implement ID Token verification.
