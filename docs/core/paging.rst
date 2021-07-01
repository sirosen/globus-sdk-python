Paging and Paginators
=====================

Globus SDK Client objects have paginated methods which return paginators.

A paginated API is one which returns data in multiple API calls.
This is used in cases where the the full set of results is too large to return all
at once, or where getting all results is slow and a few results are wanted faster.

A good example of paginated data would be search results: the first "page"
of data may be the first 10 results, and the next "page" consists of the
next 10 results.

The number of results per call is the page size.
Each page is an API response with a number of results equal to the page size.

Paging in the Globus SDK can be done by iterating over pages (responses) or by
iterating over items (individual results).

Paginators
----------

A :py:class:`~globus_sdk.paging.Paginator` object is an iterable provided by
the Globus SDK.
Paginators support iteration over pages with the method ``pages()`` and iteration
over items with the method ``items()``.

Paginators have fixed parameters which are set when the paginator is created.
Once a method returns a paginator, you don't need to pass it any additional
data -- ``pages()`` or ``items()`` will operate based on the original parameters to
the paginator.

.. _making_paginated_calls:

Making Paginated Calls
----------------------

Globus SDK client objects define paginated variants of methods. The normal
method is said to be "unpaginated", and returns a single page of results.
The paginated variant, prefixed with ``paginated.``, returns a paginated.

For example, :py:class:`~globus_sdk.TransferClient` has a paginated method,
:py:meth:`~globus_sdk.TransferClient.endpoint_search`. Once you have
a client object, calls to the unpaginated method are done like so:

.. code-block:: python

    import globus_sdk

    # for information on getting an authorizer, see the SDK Tutorial
    tc = globus_sdk.TransferClient(authorizer=...)

    # unpaginated calls can still return iterable results!
    # endpoint_search() returns an iterable response
    for endpoint_info in tc.endpoint_search("tutorial"):
        print("got endpoint_id:", endpoint_info["id"])

The paginated variant of this same method is accessed nearly identically. But
instead of calling ``endpoint_search(...)``, we'll invoke
``paginated.endpoint_search(...)``.

Here are three variants of code with the same basic effect:

.. code-block:: python

    # note the call to `items()` at the end of this line!
    for endpoint_info in tc.paginated.endpoint_search("tutorial").items():
        print("got endpoint_id:", endpoint_info["id"])

    # equivalently, call `pages()` and iterate over the items in each page
    for page in tc.paginated.endpoint_search("tutorial").pages():
        for endpoint_info in page:
            print("got endpoint_id:", endpoint_info["id"])

    # iterating on a paginator without calling `pages()` or `items()` is
    # equivalent to iterating on `pages()`
    for page in tc.paginated.endpoint_search("tutorial"):
        for endpoint_info in page:
            print("got endpoint_id:", endpoint_info["id"])

Do I need to use pages()? What is it for?
-----------------------------------------

If your use-case is satisfied with ``items()``, then stick with ``items()``!

``pages()`` iteration is important when there is useful data in the page other
than the individual items.

For example,
`~globus_sdk.TransferClient.endpoint_search <TransferClient.endpoint_search>`
returns the total number of results for the search as a field on each page.

Most use-cases can be solved with ``items()``, and ``pages()`` will be
available to you if or when you need it.

Paginator Types
---------------

``globus_sdk.paging`` defines several paginator classes and methods. For the
most part, you do not need to interact with these classes or methods except
through ``pages()`` or ``items()``.

The ``paging`` subpackage also defines the ``PaginatorTable``, which is used to
define the ``paginated`` attribute on client objects.

.. autofunction:: globus_sdk.paging.has_paginator

.. autoclass:: globus_sdk.paging.Paginator
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.PaginatorTable
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.MarkerPaginator
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.NextTokenPaginator
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.LastKeyPaginator
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.HasNextPaginator
   :members:
   :show-inheritance:

.. autoclass:: globus_sdk.paging.LimitOffsetTotalPaginator
   :members:
   :show-inheritance:
