* Add a client for the Timer service (:pr:`548`)
    * Add ``TimerClient`` class, along with ``TimerJob`` for constructing data
      to pass to the Timer service for job creation, and ``TimerAPIError``
    * Modify ``globus_sdk.config`` utilities to provide URLs for Actions and
      Timer services
