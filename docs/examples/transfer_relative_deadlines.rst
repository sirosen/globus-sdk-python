Transfer Relative Task Deadlines
--------------------------------

One of the lesser-known features of the Globus Transfer service is the ability
for users to set a ``deadline`` by which a Transfer or Delete task must
complete. If the task is still in progress when the ``deadline`` is reached,
it is aborted.

You can use this, for example, to enforce that a Transfer Task which takes too
long results in errors (even if it is making slow progress).

Because the ``deadline`` is accepted as an ISO 8601 date, you can use python's
built-in ``datetime`` library to compute a timestamp to pass to the service.

Start out by computing the current time as a ``datetime``:

.. code-block:: python

    import datetime

    now = datetime.datetime.utcnow()

Then, compute a relative timestamp using ``timedelta``:

.. code-block:: python

    future_1minute = now + datetime.timedelta(minutes=1)

This value can be passed to a :class:`TransferData <globus_sdk.TransferData>`,
as in

.. code-block:: python

    import globus_sdk

    # get various components needed for a Transfer Task
    # beyond the scope of this example
    transfer_client = globus_sdk.TransferClient(...)
    source_endpoint_uuid = ...
    dest_endpoint_uuid = ...

    # note how `future_1minute` is used here
    submission_data = globus_sdk.TransferData(
        transfer_client,
        source_endpoint_uuid,
        dest_endpoint_uuid,
        deadline=str(future_1minute),
    )
