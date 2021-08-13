import collections
import collections.abc
import hashlib
from base64 import b64encode
from enum import Enum
from typing import Any, Callable, Generator, Optional, Sequence, TypeVar, Union

from .types import IntLike, UUIDLike

T = TypeVar("T")


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_b64encode(s: Union[bytes, str]) -> str:
    if isinstance(s, str):
        encoded = b64encode(s.encode("utf-8"))
    else:
        encoded = b64encode(s)
    return encoded.decode("utf-8")


def slash_join(a: str, b: Optional[str]) -> str:
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
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


def doc_api_method(
    external_message: str,
    external_link: str,
    *,
    external_base_url: str = "https://docs.globus.org/api",
    # we could override the format string if wanted (after the normal header)
    external_format_str: str = (
        "See `{message} <{base_url}/{link}>`_ in the API documentation for details."
    ),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorate(func: Callable[..., T]) -> Callable[..., T]:
        func.__doc__ = f"""{func.__doc__}

        **External Documentation**

        """ + external_format_str.format(
            message=external_message, base_url=external_base_url, link=external_link
        )
        return func

    return decorate


def safe_stringify(value: Union[IntLike, UUIDLike]) -> str:
    """
    Converts incoming value to a unicode string. Convert bytes by decoding,
    anything else has __str__ called.
    Strings are checked to avoid duplications
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def safe_strseq_iter(value: Sequence) -> Generator[str, None, None]:
    """
    Given a Sequence (typically of strings), produce an iterator over it of strings.
    This is a passthrough with two caveats:
    - if the value is a solitary string, yield only that value
    - any value in the sequence which is not a string will be passed through
      safe_stringify

    This helps handle cases where a string is passed to a function expecting a sequence
    of strings, as well as cases where a sequence of UUID objects is accepted for a list
    of IDs, or something similar.
    """
    if isinstance(value, (str, bytes)):
        yield safe_stringify(value)
    else:
        for x in value:
            yield safe_stringify(x)


def render_enums_for_api(value: Any) -> Any:
    """
    Convert enum values to their underlying value.

    If a value is a sequence type, it will be converted to a list and the values will
    also be converted if they are enum values.
    """
    # special-case: handle str and bytes because these types are technically sequence
    # types (of bytes or str values) which could trip someone up
    if isinstance(value, (str, bytes)):
        return value
    if isinstance(value, collections.abc.Sequence):
        return [render_enums_for_api(x) for x in value]
    return value.value if isinstance(value, Enum) else value


class PayloadWrapper(collections.UserDict):
    """
    A class for defining helper objects which wrap some kind of "payload" dict.
    Typical for helper objects which formulate a request payload, e.g. as JSON.
    """

    # note: this class doesn't actually define any methods, properties, or attributes
    # it's just our own flavor of UserDict, which wraps a 'data' dict
    #
    # use UserDict rather than subclassing dict so that our API is always consistent
    # e.g. `dict.pop` does not invoke `dict.__delitem__`. Overriding `__delitem__` on a
    # dict subclass can lead to inconsistent behavior between usages like these:
    #   x = d["k"]; del d["k"]
    #   x = d.pop("k")
    #
    # UserDict inherits from MutableMapping and only defines the dunder methods, so
    # changing its behavior safely/consistently is simpler
