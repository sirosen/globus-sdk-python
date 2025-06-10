from __future__ import annotations

import collections
import collections.abc
import hashlib
import platform
import typing as t
import uuid

from globus_sdk._missing import MissingType
from globus_sdk._types import UUIDLike


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


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
