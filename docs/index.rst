.. globus-sdk-python documentation master file, created by
   sphinx-quickstart on Fri Apr  1 14:35:36 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Globus SDK for Python
=====================

This SDK provides a convenient Pythonic interface to Globus REST APIs,
including the Transfer API and the Globus Auth API. Documentation
for the REST APIs is available at https://docs.globus.org.

Two interfaces are provided - a low level interface, supporting only
``GET``, ``PUT``, ``POST``, and ``DELETE`` operations, and a high level
interface providing helper methods for common API resources.

The SDK requires python 2.6+ or 3.2+.

Basic Usage
===========

Most APIs require authentication using an access token, so the first
step to using the SDK is to acquire a token. For development, the
simplest way to get a token is to use the `Globus Tokens
<https://tokens.globus.org>`_ webapp. Globus Tokens provides you with
tokens for all Globus APIs which are valid for two days, and are tied to
a consent for ``Globus Tokens``. The appropriate method for obtaining
tokens for a production application depends on the type of application,
and is outside the scope of the SDK documentation (see the REST
documentation at https://docs.globus.org).

The webapp will provide you with instructions to save your tokens to the Globus
SDK config file, at ``~/.globus.cfg``.

To use the Transfer API:

.. code-block:: python

    from future import __print_function__ # for python 2
    from globus_sdk import TransferClient

    tc = TransferClient() # uses transfer_token from the config file

    # low level interface
    r = tc.get("/endpoint_search?filter_scope=my-endpoints")
    for epdict in r.data["DATA"]:
        print(epdict["display_name"], epdict["id"])

    # high level interface; provides iterators for list responses
    print("My Endpoints:")
    for r in tc.endpoint_search(filter_scope='my-endpoints'):
        print(r.data["display_name"], r.data["id"])

API Documentation
=================
.. toctree::
   :maxdepth: 2

   api
