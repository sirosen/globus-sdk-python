..
.. A new scriv changelog fragment
..
.. Add one or more items to the list below describing the change in clear, concise terms.
..
.. Leave the ":pr:`...`" text alone. When you open a pull request, GitHub Actions will
.. automatically replace it when the PR is merged.
..

* Add TransferRequestsTransport class that does not retry ExternalErrors. This fixes cases in which the TransferClient incorrectly retried requests (:pr:`NUMBER`)
