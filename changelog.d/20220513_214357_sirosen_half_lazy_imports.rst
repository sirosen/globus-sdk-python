* ``globus_sdk`` now defers many 3rd party imports until they are needed. This
  may lead to faster import times, but there may be a new delay when libraries
  are first used. In particular, ``requests`` can be slow to import (~100ms).
  Applications which are highly sensitive to operation latencies may prefer to
  ``import requests`` explicitly at some point during application startup to
  avoid unexpected performance spikes. (:pr:`NUMBER`)
