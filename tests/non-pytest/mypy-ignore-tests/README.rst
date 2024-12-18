Tests Using ``mypy --warn-unused-ignores``
==========================================

These tests confirm that types are correct using ``mypy
--warn-unused-ignores``.

This strategy is suggested as a lightweight test in the
`Python Typing Quality Documentation
<https://typing.readthedocs.io/en/latest/source/quality.html#testing-using-mypy-warn-unused-ignores>`_.

These tests are run by ``tox -e mypy`` from the repo root.
