import collections.abc


class Paginator(collections.abc.Iterable):
    """Base class for all paginators.
    The only thing which is guaranteed is that they are iterable."""
