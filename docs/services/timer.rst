Globus Timer
=============


.. autoclass:: globus_sdk.TimerClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

The ``TimerJob`` class is used to set up request data to send to Timer for
creating a recurring job. Currently only recurring transfers are supported.
Thus, a ``TimerJob`` should not be initialized directly; use the
``from_transfer_data`` method to construct one to start a Timer job to run a
transfer. This will require having a :class:`TransferClient
<globus_sdk.TransferClient>` instantiated first—see the Transfer service docs
for details and examples.

.. autoclass:: globus_sdk.services.timer.data.TimerJob
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a ``TimerClient`` will raise specifically a ``TimerAPIError``
rather than just a ``GlobusAPIError``.

.. autoclass:: globus_sdk.TimerAPIError
   :members:
   :show-inheritance:
