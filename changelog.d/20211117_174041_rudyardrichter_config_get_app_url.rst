..
.. A new scriv changelog fragment
..
.. Add one or more items to the list below describing the change in clear, concise terms.
..
.. Leave the ":pr:`...`" text alone. When you open a pull request, GitHub Actions will
.. automatically replace it when the PR is merged.
..

* Document ``globus_sdk.config.get_service_url`` and ``globus_sdk.config.get_webapp_url``
  (:pr:`496`)
    * Internally, these are updated to be able to default to the ``GLOBUS_SDK_ENVIRONMENT`` setting,
      so specifying an environment is no longer required
