Exceptions
==========

All Globus SDK errors inherit from ``GlobusError``, and all SDK error classes
are defined in ``globus_sdk.exc``.

It should always be safe to wrap your SDK-reliant code with something like
this::

    import logging
    from globus_sdk import exc

    try:
        tc = TransferClient()

        eps = tc.endpoint_search(filter_fulltext="myendpointsearch")

        for ep in eps:
            print(ep["display_name"])

        ...
    except exc.GlobusAPIError as e:
        # Error response from the REST service, check the code and message for
        # details.
        print("Error code", e.code)
        print("Error message", e.message)
    except exc.NetworkError as e:
        print("Network failure, check your internet connection and firewall")
    except exc.GlobusError as e:
        print("GlobusError happened when we tried to foo a bar with a baz!")
        logging.exception(e)
    else:
        ...

Of course, if you want to learn more information about the response, you should
inspect it more than this.
Malformed calls to Globus SDK methods may raise standard python exceptions
(``ValueError``, etc.), but for correct usage, all errors will be instances of
``GlobusError``.


Error Classes
-------------

.. autoclass:: globus_sdk.exc.GlobusError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.GlobusAPIError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.NetworkError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.ConnectionError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.TimeoutError
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.exc.PaginationOverrunError
   :members:
   :show-inheritance:
