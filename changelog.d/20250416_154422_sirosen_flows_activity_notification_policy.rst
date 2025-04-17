Added
~~~~~

- ``SpecificFlowClient.run_flow()`` now supports ``activity_notification_policy``
  as an argument, allowing users to select when their run will notify them. A
  new helper, ``RunActivityNotificationPolicy``, makes construction of valid
  policies easier. (:pr:`NUMBER`)
