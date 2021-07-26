from array import array
from typing import Union

from typing_extensions import Protocol

# From: https://docs.python.org/3/glossary.html#term-bytes-like-object
BytesLike = Union[array, bytes, bytearray, memoryview]


class ToStr(Protocol):
    def __str__(self) -> str:
        ...
