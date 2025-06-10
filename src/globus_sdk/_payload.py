from __future__ import annotations

import abc
import typing as t

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._remarshal import safe_strseq_iter

if t.TYPE_CHECKING:
    # pylint: disable=unsubscriptable-object
    _PayloadBaseDict = dict[str, t.Any]
else:
    _PayloadBaseDict = dict


class Payload(_PayloadBaseDict):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload.

    Payload types inheriting from this class can be passed directly to the client
    ``post()``, ``put()``, and ``patch()`` methods. These methods will
    recognize a ``PayloadBase`` and apply conversions for serialization with
    the requested encoder (e.g. as a JSON request body).
    """

    #
    # internal helpers for setting non-null values
    #

    def _set_value(
        self,
        key: str,
        val: t.Any,
        callback: t.Callable[[t.Any], t.Any] | None = None,
    ) -> None:
        """
        Internal helper for setting an omittable value on the payload.

        If the value is non-None, it will be set and the callback (if provided) will be
        invoked on it.
        Otherwise, it will be ignored and the callback will not be invoked.

        :param key: The key to set.
        :param val: The value to set.
        :param callback: An optional callback to apply to the value immediately
            before it is set.
        """
        if val is not None and val is not MISSING:
            self[key] = callback(val) if callback else val

    def _set_optstrs(self, **kwargs: t.Any) -> None:
        """
        Convenience function for setting a collection of omittable string values.

        Values are converted to strings prior to assignment.
        """
        for k, v in kwargs.items():
            self._set_value(k, v, callback=str)

    def _set_optstrlists(
        self, **kwargs: t.Iterable[t.Any] | None | MissingType
    ) -> None:
        """
        Convenience function for setting a collection of omittable string list values.

        Values are converted to lists of strings prior to assignment.
        """
        for k, v in kwargs.items():
            self._set_value(k, v, callback=lambda x: list(safe_strseq_iter(x)))

    def _set_optbools(self, **kwargs: bool | None | MissingType) -> None:
        """
        Convenience function for setting a collection of omittable bool values.

        Values are converted to bools prior to assignment.
        """
        for k, v in kwargs.items():
            self._set_value(k, v, callback=bool)

    def _set_optints(self, **kwargs: t.Any) -> None:
        """
        Convenience function for setting a collection of omittable int values.

        Values are converted to ints prior to assignment.
        """
        for k, v in kwargs.items():
            self._set_value(k, v, callback=int)


class AbstractPayload(Payload, abc.ABC):
    """
    An abstract class which is a Payload.

    This is a shim which is needed because we have a metaclass conflict between
    dict:type and ABC:ABCMeta.

    Setting the metaclass helps type checkers understand that such classes are
    abstract.
    """

    # explicitly define `__new__` in order to check for abstract methods which
    # were not redefined
    def __new__(cls, *args: t.Any, **kwargs: t.Any) -> t.Self:
        obj = super().__new__(cls, *args, **kwargs)
        abstractmethods: frozenset[str] = (
            obj.__abstractmethods__  # type: ignore[attr-defined]
        )
        if abstractmethods:
            s = "" if len(abstractmethods) == 1 else "s"
            methodnames = ", ".join(f"'{f}'" for f in abstractmethods)
            # this error very closely imitates the errors produced by ABCMeta
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} without "
                f"an implementation for abstract method{s} {methodnames}"
            )
        return obj
