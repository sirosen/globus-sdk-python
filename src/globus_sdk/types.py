import datetime
import uuid
from typing import Union

IntLike = Union[int, str]
UUIDLike = Union[uuid.UUID, str, bytes]
DateLike = Union[str, datetime.datetime]
