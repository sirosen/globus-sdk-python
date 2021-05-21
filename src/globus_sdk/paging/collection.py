import typing

from .base import Paginator

# a Paginated Method Spec is a dict which maps paginator classes to
# callables paired with dicts of parameters for the paginator
#
# e.g.
#    {
#      MarkerPaginator: [
#        (<some_method_which_can_use_marker_pagination>, {}),
#        (<other_method_which_can_use_marker_pagination>, {"setting1": True}),
#      ]
#    }
PaginatedMethodSpec = typing.Dict[
    typing.Type[Paginator],
    typing.List[typing.Tuple[typing.Callable, typing.Dict[str, typing.Any]]],
]


class PaginatorCollection:
    """
    A PaginatorCollection maps multiple methods of an SDK client to paginated variants.
    Given a method, client.foo , the collection will gain a function attribute `foo`
    (name matching is automatic) which returns a Paginator.

    So

    >>> pc = PaginatorCollection({Markerpaginator: [(client.foo, {})])  # build it
    >>> paginator = pc.foo()  # returns a paginator
    >>> for page in paginator:  # a paginator is an iterable of pages (response objects)
    >>>     print(json.dumps(page.data))  # you can handle each response object in turn

    The expected usage is to build a `paginated` attribute of a client.

    That is, if `client` has two methods `foo` and `bar` which we want paginated,

    >>> client.paginated = PaginatorCollection(client.foo, client.bar)

    and that will let us call

    >>> client.paginated.foo()
    >>> client.paginated.bar()
    """

    def __init__(self, spec: PaginatedMethodSpec):
        self._paginator_map: typing.Dict[str, typing.Callable] = {}

        for paginator_class, methodlist in spec.items():
            for bound_method, paginator_args in methodlist:
                self._add_binding(paginator_class, paginator_args, bound_method)

    # This needs to be a separate callable to work correctly as a closure over loop
    # variables
    #
    # If you try to dynamically define functions in __init__ without wrapping them like
    # this, then you run into trouble with the fact that the resulting functions will
    # point at <locals> which aren't resolved until call time
    def _add_binding(self, paginator_class, paginator_args, bound_method):
        methodname = bound_method.__name__

        def paginated_method(*args, **kwargs):
            return paginator_class(
                bound_method, client_args=args, client_kwargs=kwargs, **paginator_args
            )

        self._paginator_map[methodname] = paginated_method

    def __getattr__(self, attrname):
        try:
            return self._paginator_map[attrname]
        except KeyError:
            pass
        raise AttributeError(f"No known paginator named '{attrname}'")
