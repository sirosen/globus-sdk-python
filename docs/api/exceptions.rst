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

        eps = tc.endpoint_search(filter_fulltext='myendpointsearch')

        for ep in eps:
            print(ep.data['display_name'])

        ...
    except exc.GlobusError as e:
        print('Some GlobusError happened when we tried to foo a bar with a baz!')
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

.. autoclass:: globus_sdk.exc.PaginationOverrunError
   :members:
   :show-inheritance:
