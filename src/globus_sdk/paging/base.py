import abc
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    cast,
)

import typing_extensions as te

from globus_sdk.response import GlobusHTTPResponse

PageT = TypeVar("PageT", bound=GlobusHTTPResponse)
P = te.ParamSpec("P")
R = TypeVar("R", bound=GlobusHTTPResponse)


class Paginator(Iterable[PageT], metaclass=abc.ABCMeta):
    """
    Base class for all paginators.
    This guarantees is that they have generator methods named ``pages`` and ``items``.

    Iterating on a Paginator is equivalent to iterating on its ``pages``.

    :param method: A bound method of an SDK client, used to generate a paginated variant
    :type method: callable
    :param items_key: The key to use within pages of results to get an array of items
    :type items_key: str
    :param client_args: Arguments to the underlying method which are passed when the
        paginator is instantiated. i.e. given ``client.paginated.foo(a, b, c=1)``, this
        will be ``(a, b)``. The paginator will pass these arguments to each call of the
        bound method as it pages.
    :type client_args: tuple
    :param client_kwargs: Keyword arguments to the underlying method, like
        ``client_args`` above. ``client.paginated.foo(a, b, c=1)`` will pass this as
        ``{"c": 1}``. As with ``client_args``, it's passed to each paginated call.
    :type client_kwargs: dict
    """

    def __init__(
        self,
        method: Callable[..., Any],
        *,
        items_key: Optional[str] = None,
        client_args: List[Any],
        client_kwargs: Dict[str, Any],
        # the Base paginator must accept arbitrary additional kwargs to indicate that
        # its child classes could define and use additional kwargs
        **kwargs: Any,
    ):
        self.method = method
        self.items_key = items_key
        self.client_args = client_args
        self.client_kwargs = client_kwargs

    def __iter__(self) -> Iterator[PageT]:
        yield from self.pages()

    @abc.abstractmethod
    def pages(self) -> Iterator[PageT]:
        """``pages()`` yields GlobusHTTPResponse objects, each one representing a page
        of results."""

    def items(self) -> Iterator[Any]:
        """
        ``items()`` of a paginator is a generator which yields each item in each page of
        results.

        ``items()`` may raise a ``ValueError`` if the paginator was constructed without
        identifying a key for use within each page of results. This may be the case for
        paginators whose pages are not primarily an array of data.
        """
        if self.items_key is None:
            raise ValueError(
                "Cannot provide items() iteration on a paginator where 'items_key' "
                "is not set."
            )
        for page in self.pages():
            yield from page[self.items_key]

    @classmethod
    def wrap(cls, method: Callable[P, R]) -> Callable[P, "Paginator[R]"]:
        """
        This is an alternate method for getting a paginator for a paginated method which
        correctly preserves the type signature of the paginated method.

        It should be used on instances of clients and only passed bound methods of those
        clients. For example, given usage

            >>> tc = TransferClient()
            >>> paginator = tc.paginated.endpoint_search(...)

        a well-typed paginator can be acquired with

            >>> tc = TransferClient()
            >>> paginated_call = Paginator.wrap(tc.endpoint_search)
            >>> paginator = paginated_call(...)

        Although the syntax is slightly more verbose, this allows `mypy` and other type
        checkers to more accurately infer the type of the paginator.
        """
        # these import are deferred to avoid circular dependencies
        # `globus_sdk.paging` is needed by clients to build paginator tables
        # but the client class is needed here to be able to check that methods are
        # methods of clients
        # the table is needed here for typing, but requires Paginator
        from ..client import BaseClient

        if not inspect.ismethod(method):
            raise TypeError(f"Paginator.wrap can only be used on methods, not {method}")

        if not isinstance(method.__self__, BaseClient):
            raise ValueError(
                "Paginator.wrap can only be used on methods of globus-sdk clients"
            )

        try:
            ret = getattr(method.__self__.paginated, method.__name__)
        except AttributeError as e:
            raise ValueError(f"{method.__name__} is not a paginated method") from e

        return cast(Callable[P, Paginator[R]], ret)
