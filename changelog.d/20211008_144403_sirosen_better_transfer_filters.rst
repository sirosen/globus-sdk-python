..
.. A new scriv changelog fragment
..
.. Add one or more items to the list below describing the change in clear, concise terms.
..
.. Leave the ":pr:`...`" text alone. When you open a pull request, GitHub Actions will
.. automatically replace it in a new commit. (You can squash this commit later
.. if you like.)
..

* Add ``filter`` as a supported parameter to ``TransferClient.task_list`` (:pr:`NUMBER`)
* The ``filter`` parameter to ``TransferClient.task_list`` and
  ``TransferClient.operation_ls`` can now be passed as a ``Dict[str, str | List[str]]``.
  Documentation on the ``TransferClient`` explains how this will be formatted,
  and is linked from the param docs for ``filter`` on each method (:pr:`NUMBER`)
