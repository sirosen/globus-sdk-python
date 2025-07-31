Warnings
========

The following warnings can be emitted by the Globus SDK to indicate a
problem, or a future change, which is not necessarily an error.

.. autoclass:: globus_sdk.RemovedInV5Warning
    :members:
    :show-inheritance:


By default, Python will not display deprecation warnings to end users,
but testing frameworks like pytest will enable deprecation warnings for developers.

..  seealso::

    *   `Python's warnings module`_
    *   `pytest's warnings documentation`_


Enabling deprecation warnings
-----------------------------

By default, Python ignores deprecation warnings,
so end users of your application will not see warnings.

However, you may want to enable deprecation warnings
to help prepare for coming changes in the Globus SDK.
Deprecation warnings can be enabled in several ways:

#.  The ``PYTHONWARNINGS`` environment variable
#.  The Python executable ``-W`` argument
#.  The Python ``warnings.filterwarnings()`` function


..  rubric:: The ``PYTHONWARNINGS`` environment variable

Deprecation warnings can be enabled using this shell syntax:

..  code-block:: bash

    # POSIX shell example
    export PYTHONWARNINGS="error::DeprecationWarning"
    python ...

    # Inline example
    PYTHONWARNINGS="error::DeprecationWarning" python ...

..  code-block:: pwsh

    # Powershell example
    $env:PYTHONWARNINGS="error::DeprecationWarning"
    python ...


..  rubric:: The Python executable ``-W`` argument

Deprecation warnings can be enabled using this Python executable argument:

..  code-block:: text

    python -W "error::DeprecationWarning" ...


..  rubric:: The Python ``warnings.filterwarnings()`` function

Deprecation warnings can be enabled in Python code:

..  code-block:: python

    import warnings

    warnings.filterwarnings("error", category=DeprecationWarning)


Disabling deprecation warnings
------------------------------

Python testing frameworks like pytest enable deprecation warnings by default.
Deprecation warnings can be disabled in several ways:

#.  The ``PYTHONWARNINGS`` environment variable
#.  The pytest executable ``-W`` argument
#.  The ``pytest.ini`` (or similar) file


..  rubric:: The ``PYTHONWARNINGS`` environment variable

You can disable deprecation warnings using environment variables:

..  code-block:: bash

    # POSIX shell example
    export PYTHONWARNINGS="ignore::DeprecationWarning"
    pytest ...

    # Inline example
    PYTHONWARNINGS="ignore::DeprecationWarning" pytest ...

..  code-block:: pwsh

    # Powershell example
    $env:PYTHONWARNINGS="ignore::DeprecationWarning"
    pytest ...


..  rubric:: The pytest executable ``-W`` argument

You can disable deprecation warnings using pytest's ``-W`` argument:

..  code-block:: text

    pytest -W "ignore::DeprecationWarning" ...


..  rubric:: The ``pytest.ini`` (or similar) file

You can disable warnings using a pytest configuration file like ``pytest.ini``:

..  code-block:: ini

    [pytest]
    filterwarnings =
        ignore::DeprecationWarning


..  Links
..  -----
..  _Python's warnings module: https://docs.python.org/3/library/warnings.html
..  _pytest's warnings documentation: https://docs.pytest.org/en/latest/how-to/capture-warnings.html
