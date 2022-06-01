Globus Timer
=============

.. currentmodule:: globus_sdk

.. autoclass:: TimerClient
   :members:
   :member-order: bysource
   :show-inheritance:
   :exclude-members: error_class

Helper Objects
--------------

The :class:`TimerJob` class is used to set up request data to send to Timer for
creating a recurring job. Currently only recurring transfers are supported.
Thus, a :class:`TimerJob` should not be initialized directly; use the
:meth:`TimerJob.from_transfer_data` method to construct one to start a Timer job to run a
transfer. This will require having a :class:`TransferClient`
nstantiated first -- see the Transfer service docs
for details and examples.

.. autoclass:: TimerJob
   :members:
   :show-inheritance:

Client Errors
-------------

When an error occurs, a :class:`TimerClient` will raise specifically a `TimerAPIError`
rather than just a :class:`GlobusAPIError`.

.. autoclass:: TimerAPIError
   :members:
   :show-inheritance:
