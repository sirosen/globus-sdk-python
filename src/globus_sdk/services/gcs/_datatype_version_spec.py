# an internal module for parsing document version specifications on DATA_TYPE
import collections
import re
from typing import Tuple, cast

VALID_SPEC_RE = re.compile(
    r"""
    (\w+)  # name
    (
        (==\d+(\.\d+)*)  |  # ==N
        (>=?\d+(\.\d+)*) |  # >N >=N
        (<=?\d+(\.\d+)*) |  # <N <=N
        (>=?\d+(\.\d+)*,<=?\d+(\.\d+)*)  # >N,<M >=N,<M >N,<=M >=N,<=M
    )
    """,
    flags=re.VERBOSE,
)


# an upper, lower, or exact bound on a version, specified as
# a version triple + inclusive=t/f
BoundSpec = collections.namedtuple("BoundSpec", ("v", "inclusive"))


def _to_triple(v: str) -> Tuple[int, int, int]:
    xs = v.split(".")
    if len(xs) > 3:
        raise ValueError("Datatype Versions with more than 3 digits are not supported.")
    while len(xs) < 3:
        xs.append("0")
    return cast(Tuple[int, int, int], tuple(int(x) for x in xs))


def _parse_bound(raw_bound: str, prefixchar: str) -> BoundSpec:
    inclusive_prefix = prefixchar + "="  # ">" -> ">="
    inclusive = raw_bound.startswith(inclusive_prefix)
    stripped_bound = raw_bound.lstrip(inclusive_prefix)
    return BoundSpec(v=_to_triple(stripped_bound), inclusive=inclusive)


class DatatypeVersionRange:
    def __init__(self, specstr: str):
        match = VALID_SPEC_RE.fullmatch(specstr)
        if not match:
            raise ValueError(f"Failed to parse version spec '{specstr}'")
        self.name = match.group(1)
        constraint = match.group(2)

        self.lower = None
        self.upper = None
        self.exact = None
        if "," in constraint:
            low, high = constraint.split(",", 1)
            self.lower = _parse_bound(low, ">")
            self.upper = _parse_bound(high, "<")
        elif constraint.startswith("=="):
            self.exact = _parse_bound(constraint, "=")
        elif constraint.startswith(">"):
            self.lower = _parse_bound(constraint, ">")
        else:
            self.upper = _parse_bound(constraint, "<")

        if self.lower and self.upper:
            if self.lower.v >= self.upper.v:
                raise ValueError("Invalid version spec, lower >= upper")

    def _version_match(self, other: str) -> bool:
        try:
            parsed = tuple(int(x) for x in other.split("."))
        except ValueError:
            return False
        if len(parsed) != 3:
            return False

        # check lower bound
        if self.lower:
            if parsed < self.lower.v:
                return False
            if parsed == self.lower.v and not self.lower.inclusive:
                return False

        # check upper bound
        if self.upper:
            if parsed > self.upper.v:
                return False
            if parsed == self.upper.v and not self.upper.inclusive:
                return False

        # check an exact constraint
        if self.exact and parsed != self.exact.v:
            return False

        return True

    def matches(self, data_type: str) -> bool:
        if "#" not in data_type:  # invalid, guard against strings with no version
            return False
        name, version = data_type.split("#", 1)
        return name == self.name and self._version_match(version)
