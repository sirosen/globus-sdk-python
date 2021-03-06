Recursive ``ls`` via TransferClient
-----------------------------------

The Globus Transfer API does not offer a recursive variant of the ``ls``
operation. There are several reasons for this, but most obviously: ``ls`` is
synchronous, and a recursive listing may be very slow.

This example demonstrates how to write a breadth-first traversal of a dir tree
using a local deque to implement recursive ``ls``. You will need a properly
authenticated :class:`TransferClient <globus_sdk.TransferClient>`.

.. code-block:: python

    from collections import deque


    def _recursive_ls_helper(tc, ep, queue, max_depth):
        while queue:
            abs_path, rel_path, depth = queue.pop()
            path_prefix = rel_path + "/" if rel_path else ""

            res = tc.operation_ls(ep, path=abs_path)

            if depth < max_depth:
                queue.extend(
                    (
                        res["path"] + item["name"],
                        path_prefix + item["name"],
                        depth + 1,
                    )
                    for item in res["DATA"]
                    if item["type"] == "dir"
                )
            for item in res["DATA"]:
                item["name"] = path_prefix + item["name"]
                yield item


    # tc: a TransferClient
    # ep: an endpoint ID
    # path: the path to list recursively
    def recursive_ls(tc, ep, path, max_depth=3):
        queue = deque()
        queue.append((path, "", 0))
        yield from _recursive_ls_helper(tc, ep, queue, max_depth)


This acts as a generator function, which you can then use for iteration, or
evaluate with ``list()`` or other expressions which will iterate over values
from the generator.

adding sleep
~~~~~~~~~~~~

One of the issues with the above recursive listing tooling is that it can
easily run into rate limits on very large dir trees with a fast filesystem.

To avoid issues, simply add a periodic sleep. For example, we could add a
``sleep_frequency`` and ``sleep_duration``, then count the number of ``ls``
calls that have been made. Every ``sleep_frequency`` calls, sleep for
``sleep_duration``.

The modifications in the helper would be something like so:

.. code-block:: python

    import time


    def _recursive_ls_helper(tc, ep, queue, max_depth, sleep_frequency, sleep_duration):
        call_count = 0
        while queue:
            abs_path, rel_path, depth = queue.pop()
            path_prefix = rel_path + "/" if rel_path else ""

            res = tc.operation_ls(ep, path=abs_path)

            call_count += 1
            if call_count % sleep_frequency == 0:
                time.sleep(sleep_duration)

            # as above
            ...


parameter passthrough
~~~~~~~~~~~~~~~~~~~~~

What if you want to pass parameters to the ``ls`` calls? Accepting that some
behaviors -- like order-by -- might not behave as expected if passed to the
recursive calls, you can still do-so. Add ``ls_params``, a dictionary of
additional parameters to pass to the underlying ``operation_ls`` invocations.

The helper can assume that a dict is passed, and the wrapper would just
initialize it as ``{}`` if nothing is passed.

Something like so:

.. code-block:: python

    def _recursive_ls_helper(tc, ep, queue, max_depth, ls_params):
        call_count = 0
        while queue:
            abs_path, rel_path, depth = queue.pop()
            path_prefix = rel_path + "/" if rel_path else ""

            res = tc.operation_ls(ep, path=abs_path, **ls_params)

            # as above
            ...


    # importantly, the params should default to `None` and be rewritten to a
    # dict in the function body (parameter default bindings are modifiable)
    def recursive_ls(tc, ep, path, max_depth=3, ls_params=None):
        ls_params = ls_params or {}
        queue = deque()
        queue.append((path, "", 0))
        yield from _recursive_ls_helper(
            tc, ep, queue, max_depth, sleep_frequency, sleep_duration, ls_params
        )

What if we want to have different parameters to the top-level ``ls`` call from
any of the recursive calls? For example, maybe we want to filter the items
found in the initial directory, but not in subdirectories.

In that case, we just add on another layer: ``top_level_ls_params``, and we
only use those parameters on the initial call.

.. code-block:: python

    def _recursive_ls_helper(
        tc,
        ep,
        queue,
        max_depth,
        ls_params,
        top_level_ls_params,
    ):
        first_call = True
        while queue:
            abs_path, rel_path, depth = queue.pop()
            path_prefix = rel_path + "/" if rel_path else ""

            use_params = ls_params
            if first_call:
                # on modern pythons, dict expansion can be used to easily
                # combine dicts
                use_params = {**ls_params, **top_level_ls_params}
                first_call = False
            res = tc.operation_ls(ep, path=abs_path, **use_params)

            # again, the rest of the loop is the same
            ...


    def recursive_ls(
        tc,
        ep,
        path,
        max_depth=3,
        ls_params=None,
        top_level_ls_params=None,
    ):
        ls_params = ls_params or {}
        top_level_ls_params = top_level_ls_params or {}
        ...


With Sleep and Parameter Passing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can combine sleeps and parameter passing into one final, complete example:

.. code-block:: python

    import time
    from collections import deque


    def _recursive_ls_helper(
        tc,
        ep,
        queue,
        max_depth,
        sleep_frequency,
        sleep_duration,
        ls_params,
        top_level_ls_params,
    ):
        call_count = 0
        while queue:
            abs_path, rel_path, depth = queue.pop()
            path_prefix = rel_path + "/" if rel_path else ""

            use_params = ls_params
            if call_count == 0:
                use_params = {**ls_params, **top_level_ls_params}

            res = tc.operation_ls(ep, path=abs_path, **use_params)

            call_count += 1
            if call_count % sleep_frequency == 0:
                time.sleep(sleep_duration)

            if depth < max_depth:
                queue.extend(
                    (
                        res["path"] + item["name"],
                        path_prefix + item["name"],
                        depth + 1,
                    )
                    for item in res["DATA"]
                    if item["type"] == "dir"
                )
            for item in res["DATA"]:
                item["name"] = path_prefix + item["name"]
                yield item


    def recursive_ls(
        tc,
        ep,
        path,
        max_depth=3,
        sleep_frequency=10,
        sleep_duration=0.5,
        ls_params=None,
        top_level_ls_params=None,
    ):
        ls_params = ls_params or {}
        top_level_ls_params = top_level_ls_params or {}
        queue = deque()
        queue.append((path, "", 0))
        yield from _recursive_ls_helper(
            tc,
            ep,
            queue,
            max_depth,
            sleep_frequency,
            sleep_duration,
            ls_params,
            top_level_ls_params,
        )
