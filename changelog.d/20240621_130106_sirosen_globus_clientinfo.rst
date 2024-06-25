Added
~~~~~

- Clients will now emit a ``X-Globus-Client-Info`` header which reports the
  version of the ``globus-sdk`` which was used to send a request. Users may
  customize this header further by modifying the ``globus_clientinfo`` object
  attached to the transport object. (:pr:`990`)
