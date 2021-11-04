..
.. A new scriv changelog fragment
..
.. Add one or more items to the list below describing the change in clear, concise terms.
..
.. Leave the ":pr:`...`" text alone. When you open a pull request, GitHub Actions will
.. automatically replace it when the PR is merged.
..

* Add the `resource_server` property to client classes and objects. For example,
  `TransferClient.resource_server` and `GroupsClient().resource_server` are now usable
  to get the resource server string for the relevant services. `resource_server` is
  documented as part of `globus_sdk.BaseClient` and may be `None`. (:pr:`NUMBER`)
