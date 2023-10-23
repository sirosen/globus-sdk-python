from __future__ import annotations

import datetime
import logging
import typing as t

from globus_sdk.config import get_service_url
from globus_sdk.exc import warn_deprecated
from globus_sdk.services.transfer import TransferData
from globus_sdk.utils import PayloadWrapper, slash_join

log = logging.getLogger(__name__)


class TransferTimer(PayloadWrapper):
    """
    A helper for specifying the payload for Transfer Timer creation.
    Use this along with :meth:`create_timer <globus_sdk.TimerClient.create_timer>` to
    create a timer.

    .. note::
        ``TimerClient`` has two methods for creating timers, ``create_timer`` and
        ``create_job``.
        ``create_job`` uses a different API -- only ``create_timer`` will work with
        this helper class.

        Users are strongly recommended to use ``create_timer`` and this helper for
        timer creation.

    :param name: A name to identify this timer
    :type name: str, optional
    :param schedule: The schedule on which the timer runs
    :type schedule: dict
    :param body: A transfer payload for the timer to use. If it includes
        ``submission_id`` or ``skip_activation_check``, these parameters will be
        removed, as they are not supported in timers.
    :type body: dict or :class:`~.TransferData`

    The Schedule field encodes data which determines when the Timer will run.
    Timers may be "run once" or "recurring", and "recurring" timers may specify an end
    date or a number of executions after which the timer will stop.
    Example schedules:

    .. tab-set::

        .. tab-item:: Run Once, Right Now

            .. code-block:: python

                schedule = {"type": "once"}

        .. tab-item:: Run Once, At a Specific Time

            .. code-block:: python

                schedule = {"type": "once", "datetime": "2023-09-22T00:00:00Z"}

        .. tab-item:: Run Every 5 Minutes, Until a Specific Time

            .. code-block:: python

                schedule = {
                    "type": "recurring",
                    "interval_seconds": 300,
                    "end": {"condition": "time", "datetime": "2023-10-01T00:00:00Z"},
                }

        .. tab-item:: Run Every 30 Minutes, 10 Times

            .. code-block:: python

                schedule = {
                    "type": "recurring",
                    "interval_seconds": 1800,
                    "end": {"condition": "iterations", "iterations": 10},
                }

        .. tab-item:: Run Every 10 Minutes, Indefinitedly

            .. code-block:: python

                schedule = {"type": "recurring", "interval_seconds": 600}
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        schedule: dict[str, t.Any],
        body: dict[str, t.Any] | TransferData,
    ) -> None:
        super().__init__()
        self["timer_type"] = "transfer"
        self["name"] = name
        self["schedule"] = schedule
        self["body"] = self._preprocess_body(body)

    def _preprocess_body(
        self, body: dict[str, t.Any] | TransferData
    ) -> dict[str, t.Any]:
        # shallow-copy for dicts, convert any TransferData to a dict
        new_body = dict(body)
        # remove the skip_activation_check and submission_id parameters unconditionally
        # (not supported in timers, but often present in TransferData)
        new_body.pop("submission_id", None)
        new_body.pop("skip_activation_check", None)
        return new_body


class TimerJob(PayloadWrapper):
    r"""
    .. warning::

        This method of specifying and creating Timers for data transfer is now
        deprecated. Users should use ``TimerData`` instead.

        ``TimerJob`` is still supported for non-transfer use-cases.

    Helper for specifying a timer in the Timer service. Used as the ``data``
    argument in :meth:`create_job <globus_sdk.TimerClient.create_job>`.

    The ``callback_url`` parameter should always be the URL used to run an
    action provider.

    :param callback_url: URL for the action which the Timer job will use.
    :type callback_url: str
    :param callback_body: JSON data which Timer will send to the Action Provider on
        each invocation
    :type callback_body: dict
    :param start: The datetime at which to start the Timer job.
    :type start: datetime.datetime or str
    :param interval: The interval at which the Timer job should recur. Interpreted as
        seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the job is
        set to run only a single time, then interval *must* be None.
    :type interval: datetime.timedelta or int
    :param name: A (not necessarily unique) name to identify this job in Timer
    :type name: str, optional
    :param stop_after: A date after which the Timer job will stop running
    :type stop_after: datetime.datetime, optional
    :param stop_after_n: A number of executions after which the Timer job will stop
    :type stop_after_n: int
    :param scope: Timer defaults to the Transfer 'all' scope. Use this parameter to
        change the scope used by Timer when calling the Transfer Action Provider.
    :type scope: str, optional

    .. automethodlist:: globus_sdk.TimerJob
    """

    def __init__(
        self,
        callback_url: str,
        callback_body: dict[str, t.Any],
        start: datetime.datetime | str,
        interval: datetime.timedelta | int | None,
        *,
        name: str | None = None,
        stop_after: datetime.datetime | None = None,
        stop_after_n: int | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__()
        self["callback_url"] = callback_url
        self["callback_body"] = callback_body
        if isinstance(start, datetime.datetime):
            self["start"] = start.isoformat()
        else:
            self["start"] = start
        if isinstance(interval, datetime.timedelta):
            self["interval"] = int(interval.total_seconds())
        else:
            self["interval"] = interval
        if name is not None:
            self["name"] = name
        if stop_after is not None:
            self["stop_after"] = stop_after.isoformat()
        if stop_after_n is not None:
            self["stop_after_n"] = stop_after_n
        if scope is not None:
            self["scope"] = scope

    @classmethod
    def from_transfer_data(
        cls,
        transfer_data: TransferData | dict[str, t.Any],
        start: datetime.datetime | str,
        interval: datetime.timedelta | int | None,
        *,
        name: str | None = None,
        stop_after: datetime.datetime | None = None,
        stop_after_n: int | None = None,
        scope: str | None = None,
        environment: str | None = None,
    ) -> TimerJob:
        r"""
        Specify data to create a Timer job using the parameters for a transfer. Timer
        will use those parameters to run the defined transfer operation, recurring at
        the given interval.

        :param transfer_data: A :class:`TransferData <globus_sdk.TransferData>` object.
            Construct this object exactly as you would normally; Timer will use this to
            run the recurring transfer.
        :type transfer_data: globus_sdk.TransferData
        :param start: The datetime at which to start the Timer job.
        :type start: datetime.datetime or str
        :param interval: The interval at which the Timer job should recur. Interpreted
            as seconds if specified as an integer. If ``stop_after_n == 1``, i.e. the
            job is set to run only a single time, then interval *must* be None.
        :type interval: datetime.timedelta or int
        :param name: A (not necessarily unique) name to identify this job in Timer
        :type name: str, optional
        :param stop_after: A date after which the Timer job will stop running
        :type stop_after: datetime.datetime, optional
        :param stop_after_n: A number of executions after which the Timer job will stop
        :type stop_after_n: int
        :param scope: Timer defaults to the Transfer 'all' scope. Use this parameter to
            change the scope used by Timer when calling the Transfer Action Provider.
        :type scope: str, optional
        :param environment: For internal use: because this method needs to generate a
            URL for the Transfer Action Provider, this argument can control which
            environment the Timer job is sent to.
        :type environment: str, optional
        """
        warn_deprecated(
            "TimerJob.from_transfer_data(X, ...) is deprecated. "
            "Prefer TransferTimer(body=X, ...) instead."
        )

        transfer_action_url = slash_join(
            get_service_url("actions", environment=environment), "transfer/transfer/run"
        )
        log.info(
            "Creating TimerJob from TransferData, action_url=%s", transfer_action_url
        )
        for key in ("submission_id", "skip_activation_check"):
            if key in transfer_data:
                raise ValueError(
                    f"cannot create TimerJob from TransferData which has {key} set"
                )
        # dict will either convert a `TransferData` object or leave us with a dict here
        callback_body = {"body": dict(transfer_data)}
        return cls(
            transfer_action_url,
            callback_body,
            start,
            interval,
            name=name,
            stop_after=stop_after,
            stop_after_n=stop_after_n,
            scope=scope,
        )
