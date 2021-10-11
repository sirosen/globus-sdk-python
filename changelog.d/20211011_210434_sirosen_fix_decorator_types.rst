..
.. A new scriv changelog fragment
..
.. Add one or more items to the list below describing the change in clear, concise terms.
..
.. Leave the ":pr:`...`" text alone. When you open a pull request, GitHub Actions will
.. automatically replace it when the PR is merged.
..

* Fix several internal decorators which were destroying type information about
  decorated functions. Type signatures of many methods are therefore corrected (:pr:`485`)
