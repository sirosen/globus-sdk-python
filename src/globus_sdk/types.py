# this module only imports from `typing` at runtime
# this ensures that we don't slow down import times trying to import
# potentially heavyweight modules in order to get good type annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import datetime
    import uuid

IntLike = Union[int, str]
UUIDLike = Union["uuid.UUID", str]
DateLike = Union[str, "datetime.datetime"]
