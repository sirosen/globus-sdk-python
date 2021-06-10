Globus SDK for Python
=====================

This SDK provides a convenient Pythonic interface to
`Globus <https://www.globus.org>`_ web APIs,
including the Transfer API and the Globus Auth API. Documentation
for the APIs is available at https://docs.globus.org/api/.

Two interfaces are provided - a low level interface, supporting only
``GET``, ``PUT``, ``POST``, and ``DELETE`` operations, and a high level
interface providing helper methods for common API resources.

Additionally, some tools for interacting with local endpoint definitions are
provided.

Source code is available at https://github.com/globus/globus-sdk-python.

Table of Contents
-----------------

.. toctree::
    :caption: Getting Started
    :maxdepth: 1

    installation
    tutorial

.. toctree::
    :caption: Full Reference
    :maxdepth: 2

    services/index
    local_endpoints
    authorization
    tokenstorage
    config
    core/index

.. toctree::
    :caption: Additional Info
    :maxdepth: 1

    versioning
    license

.. toctree::
    :caption: Examples
    :maxdepth: 1

    examples/index
