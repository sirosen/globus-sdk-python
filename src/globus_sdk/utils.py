from __future__ import annotations

import collections
import collections.abc
import hashlib
import platform
import typing as t
import uuid
from base64 import b64encode

from globus_sdk._missing import MISSING, MissingType
from globus_sdk._types import UUIDLike

if t.TYPE_CHECKING:
    # pylint: disable=unsubscriptable-object
    PayloadWrapperBase = collections.UserDict[str, t.Any]
else:
    PayloadWrapperBase = collections.UserDict


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def b64str(s: str) -> str:
    return b64encode(s.encode("utf-8")).decode("utf-8")


def get_nice_hostname() -> str | None:
    """
    Get the current hostname, with the following added behavior:

    - if it ends in '.local', strip that suffix, as this is a frequent macOS behavior
      'DereksCoolMacbook.local' -> 'DereksCoolMacbook'

    - if the hostname is undiscoverable, return None
    """
    name = platform.node()
    if name.endswith(".local"):
        return name[: -len(".local")]
    return name or None


def slash_join(a: str, b: str | None) -> str:
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.

    :param a: the first path component
    :param b: the second path component
    """
    if not b:  # "" or None, don't append a slash
        return a
    if a.endswith("/"):
        if b.startswith("/"):
            return a[:-1] + b
        return a + b
    if b.startswith("/"):
        return a + b
    return a + "/" + b


def safe_strseq_iter(
    value: t.Iterable[t.Any] | str | uuid.UUID,
) -> t.Iterator[str]:
    """
    Given an Iterable (typically of strings), produce an iterator over it of strings.

    :param value: The stringifiable object or objects to iterate over

    This is a passthrough with some caveats:
    - if the value is a solitary string, yield only that value
    - if the value is a solitary UUID, yield only that value (as a string)
    - str values in the iterable which are not strings

    This helps handle cases where a string is passed to a function expecting an iterable
    of strings, as well as cases where an iterable of UUID objects is accepted for a
    list of IDs, or something similar.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, uuid.UUID):
        yield str(value)
    else:
        for x in value:
            yield str(x)


def commajoin(val: UUIDLike | t.Iterable[UUIDLike] | MissingType) -> str | MissingType:
    # note that this explicit handling of Iterable allows for string-like objects to be
    # passed to this function and be stringified by the `str()` call
    if isinstance(val, MissingType):
        return val
    if isinstance(val, collections.abc.Iterable):
        return ",".join(safe_strseq_iter(val))
    return str(val)


class PayloadWrapper(PayloadWrapperBase):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload, e.g. as JSON.

    Payload types inheriting from this class can be passed directly to the client
    ``post()``, ``put()``, and ``patch()`` methods instead of a dict. These methods will
    recognize a ``PayloadWrapper`` and convert it to a dict for serialization with the
    requested encoder (e.g. as a JSON request body).
    """

    # use UserDict rather than subclassing dict so that our API is always consistent
    # e.g. `dict.pop` does not invoke `dict.__delitem__`. Overriding `__delitem__` on a
    # dict subclass can lead to inconsistent behavior between usages like these:
    #   x = d["k"]; del d["k"]
    #   x = d.pop("k")
    #
    # UserDict inherits from MutableMapping and only defines the dunder methods, so
    # changing its behavior safely/consistently is simpler

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
