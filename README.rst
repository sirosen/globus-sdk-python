.. image:: https://travis-ci.org/globus/globus-sdk-python.svg?branch=master
    :alt: build status
    :target: https://travis-ci.org/globus/globus-sdk-python

.. image:: https://img.shields.io/pypi/v/globus-sdk.svg
    :alt: Latest Released Version
    :target: https://pypi.org/project/globus-sdk/

.. image:: https://img.shields.io/pypi/pyversions/globus-sdk.svg
    :alt: Supported Python Versions
    :target: https://pypi.org/project/globus-sdk/

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :alt: License
    :target: https://opensource.org/licenses/Apache-2.0


Globus SDK for Python
=====================

This SDK provides a convenient Pythonic interface to
`Globus <https://www.globus.org>`_ APIs.

Basic Usage
-----------

Install with ``pip install globus-sdk``

You can then import Globus client classes and other helpers from
``globus_sdk``. For example:

.. code-block:: python

    from globus_sdk import LocalGlobusConnectPersonal

    # None if Globus Connect Personal is not installed
    endpoint_id = LocalGlobusConnectPersonal().endpoint_id


Testing, Development, and Contributing
--------------------------------------

Go to the
`CONTRIBUTING <https://github.com/globus/globus-sdk-python/blob/master/CONTRIBUTING.adoc>`_
guide for detail.

Links
-----
| Full Documentation: http://globus-sdk-python.readthedocs.io/
| Source Code: https://github.com/globus/globus-sdk-python
| API Documentation: https://docs.globus.org/api/
| Release History + Changelog: https://github.com/globus/globus-sdk-python/releases
