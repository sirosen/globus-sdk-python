import typing

from .base import Paginator

# a Paginated Method Spec is a dict which maps paginator classes to
# method names paired with dicts of parameters for the paginator
#
# the parameter dict may also be omitted
#
# e.g.
#    {
#      MarkerPaginator: [
#        ("foo", {}),
#        ("bar", {"setting1": True}),
#        "baz",
#      ]
#    }
PaginatedMethodSpec = typing.Dict[
    typing.Type[Paginator],
    typing.List[
        typing.Union[
            str,
            typing.Tuple[typing.Union[str], typing.Dict[str, typing.Any]],
        ]
    ],
]


class PaginatorTable:
    """
    A PaginatorTable maps multiple methods of an SDK client to paginated variants.
    Given a method, client.foo , the collection will gain a function attribute `foo`
    (name matching is automatic) which returns a Paginator.

    So

    >>> pc = PaginatorTable(client_object, {MarkerPaginator: ["foo"]})
    >>> paginator = pc.foo()  # returns a paginator
    >>> for page in paginator:  # a paginator is an iterable of pages (response objects)
    >>>     print(json.dumps(page.data))  # you can handle each response object in turn

    The expected usage is to build a `paginated` attribute of a client.

    That is, if `client` has two methods `foo` and `bar` which we want paginated,

    >>> client.paginated = PaginatorTable(
    >>>     client, {MarkerPaginator: ["foo", "bar"]}
    >>> )

    and that will let us call

    >>> client.paginated.foo()
    >>> client.paginated.bar()

    This is done automatically as part of client instantiation, and is never meant to be
    run manually.
    """

    def __init__(self, has_methods: typing.Any, spec: PaginatedMethodSpec):
        self._paginator_map: typing.Dict[str, typing.Callable] = {}

        for paginator_class, methodlist in spec.items():
            for bindinginfo in methodlist:
                if isinstance(bindinginfo, tuple):
                    method, paginator_args = bindinginfo
                else:
                    method, paginator_args = bindinginfo, {}

                self._add_binding(has_methods, paginator_class, paginator_args, method)

    # This needs to be a separate callable to work correctly as a closure over loop
    # variables
    #
    # If you try to dynamically define functions in __init__ without wrapping them like
    # this, then you run into trouble with the fact that the resulting functions will
    # point at <locals> which aren't resolved until call time
    def _add_binding(self, has_methods, paginator_class, paginator_args, methodname):
        bound_method = getattr(has_methods, methodname)

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
