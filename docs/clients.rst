.. _clients:

Service Clients
===============

The Globus SDK provides a client class for every public Globus API.
Each client object takes authentication credentials from config files,
environment variables, or programmatically via :ref:`GlobusAuthorizers <authorization>`.

Once instantiated, a Client gives you high-level interface to make API calls,
without needing to know Globus API endpoints or their various parameters.

For example, you could use the ``TransferClient`` to list your task history
very simply::

    from globus_sdk import TransferClient, AccessTokenAuthorizer

    # you must have a valid transfer token for this to work
    tc = TransferClient(
        authorizer=AccessTokenAuthorizer("TRANSFER_TOKEN_STRING")
    )

    print("My Last 25 Tasks:")
    # `filter` to get Delete Tasks (default is just Transfer Tasks)
    for task in tc.task_list(num_results=25, filter="type:TRANSFER,DELETE"):
        print(task["task_id"], task["type"], task["status"])

.. rubric:: Multi-Thread and Multi-Process Safety

Each Globus SDK client class holds a networking session object to interact
with the Globus API. Using a previously created service client object after
forking or between multiple threads should be considered unsafe. In
multi-processing applications, it is recommended to create service client
objects after process forking and to ensure that there is only one service
client instance created per process.

.. rubric:: Client Types

:doc:`clients/base`
    All clients have a common core defined by the Base Client.
    The Base Client provides methods which are accessible via any client
    object. These methods correspond directly to HTTP verbs and represent
    single HTTP requests.

    For example, ``get()`` is a method of ``TransferClient`` and ``AuthClient``
    objects, and for each of those it sends an HTTP ``GET`` to the target
    service.

:doc:`clients/auth`
    Using Globus Auth in the SDK is done via several different client types
    which represent different types of applications.

    Additionally, there are objects for managing OAuth2 login flows and
    customized responses which make it easier to unpack token responses.

    The Globus Auth interface also includes the :class:`IdentityMap <globus_sdk.IdentityMap>`
    object, which helps manage bulk identity lookups.

:doc:`clients/transfer`
    The Globus Transfer API is usable in the SDK through the
    :class:`TransferClient <globus_sdk.TransferClient>` object.

    Additionally, there are helper objects for assembling Transfer and Delete
    Task data for submission to the service.

    Customized response types simplify handling of paginated response data,
    producing iterables of the underlying response types.

:doc:`clients/search`
    The Globus Search API is usable in the SDK through the
    :class:`SearchClient <globus_sdk.SearchClient>` object.

    Additionally, there is a :class:`SearchQuery <globus_sdk.SearchQuery>`
    object which provides a chainable API for building query documents.
