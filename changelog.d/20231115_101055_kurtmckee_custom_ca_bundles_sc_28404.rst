Added
~~~~~

- Support custom CA certificate bundles. (:pr:`903`)

  Previously, SSL/TLS verification allowed only a boolean ``True`` or ``False`` value.
  It is now possible to specify a CA certificate bundle file
  using the existing ``verify_ssl`` parameter
  or ``GLOBUS_SDK_VERIFY_SSL`` environment variable.

  This may be useful for interacting with Globus through certain proxy firewalls.
