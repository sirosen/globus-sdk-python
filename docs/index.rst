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
GET, PUT, POST, and DELETE operations, and a high level interface providing
helper methods for common API resources.

The SDK requires python 2.6+ or 3.2+.

Basic Usage
===========

Most APIs require authentication using an access token, so the first step
to using the SDK is to acquire a token. For now the simplest way to get a
token is to use the legacy Nexus Goauth API, which requires a globusid.org
identity::

    >>> from globus_sdk import NexusClient
    >>> from getpass import getpass
    >>> username = "globusid_username"
    >>> password = getpass()
    >>> nc = NexusClient()
    >>> token = nc.get_goauth_token(username, password)
    >>> with open(os.path.expanduser("~/.globus.cfg"), "w") as f:
    ...     f.write('auth_token = "%s"\n' % token)

This saves the token to '.globus.cfg' in the user's home directory, which is
sourced by default by all SDK clients, so it only needs to be done once.

To use the Transfer API:

    >>> from future import __print_function__ # for python 2
    >>> from globus_sdk import TransferClient
    >>> tc = TransferClient() # uses token from the config file
    >>> # low level interface
    >>> r = tc.get("/endpoint_search?filter_scope=my-endpoints")
    >>> for epdict in r.data["DATA"]:
    >>>     print(epdict["display_name"], epdict["id"])

    >>> # high level interface; provides iterators for list responses
    >>> print("My Endpoints:")
    >>> for r in tc.endpoint_search(filter_scope='my-endpoints'):
    >>>     print(r.data["display_name"], r.data["id"])

API Documentation
=================
.. toctree::
   :maxdepth: 2

   api
