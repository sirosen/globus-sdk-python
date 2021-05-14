Globus SDK Configuration
========================

The behaviors of the SDK can be controlled either through environment variables,
or by passing parameters to clients and other objects.

.. note::

    SDK v1.x and v2.x supported the use of `/etc/globus.cfg` and
    `~/.globus.cfg` to set certain values. This feature was removed in v3.0 in
    favor of new environment variables for setting these values.

Environment Variables
---------------------

Each of these environment variables will be read automatically by the SDK.

Environment variables have lower precedence than explicit values set in
the interpreter. If ``GLOBUS_SDK_VERIFY_SSL="false"`` is set and a client is
created with ``verify_ssl=True``, the resulting client will have SSL
verification turned on.

``GLOBUS_SDK_VERIFY_SSL``
    Used to disable SSL verification, typically to handle SSL-intercepting
    firewalls. By default, all connections to servers are verified. Set
    ``GLOBUS_SDK_VERIFY_SSL="false"`` to disable verification.

``GLOBUS_SDK_HTTP_TIMEOUT``
    Adjust the timeout when HTTP requests are made. By default, requests have a
    60 second read timeout -- for slower responses, try setting
    ``GLOBUS_SDK_HTTP_TIMEOUT=120``

``GLOBUS_SDK_ENVIRONMENT``
    The name of the environment to use. Set ``GLOBUS_SDK_ENVIRONMENT="preview"``
    to use the Globus Preview environment. (Primarily for internal use.)
