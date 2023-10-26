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

The main helper users should use is the one for constructing Transfer Timers:

.. autoclass:: TransferTimer
   :members:
   :show-inheritance:

In order to schedule a timer, pass a ``schedule`` with relevant parameters.
This can be done using the two schedule helper classes

.. autoclass:: OnceTimerSchedule
   :members:
   :show-inheritance:

.. autoclass:: RecurringTimerSchedule
   :members:
   :show-inheritance:

TimerJob (legacy)
~~~~~~~~~~~~~~~~~

The ``TimerJob`` class is still supported for creating timer, but it is
not recommended.
New users should prefer the ``TransferTimer`` class.

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
