"""
Experimental: a mypy plugin for special types within the Globus SDK
"""

import typing as t

from mypy.nodes import MDEF, TypeInfo
from mypy.plugin import AttributeContext, Plugin
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    ProperType,
    Type,
    TypeOfAny,
    get_proper_type,
)

PAGINATOR_NAME = "globus_sdk.paging.base.Paginator"
PAGINATOR_TABLE_NAME = "globus_sdk.paging.table.PaginatorTable"


class GlobusSDKPlugin(Plugin):
    def _get_paginator_type(self) -> ProperType:
        symbol = self.lookup_fully_qualified(PAGINATOR_NAME)
        if symbol and isinstance(symbol.node, TypeInfo):
            return Instance(symbol.node, [])
        return AnyType(TypeOfAny.special_form)

    def _get_attribute_type(
        self, typ: ProperType, attr_name: str
    ) -> t.Optional[ProperType]:
        symbol = self.lookup_fully_qualified(f"{typ}.{attr_name}")
        if not symbol:
            return None
        if symbol.kind != MDEF:
            return None
        # use type-ignore comments to avoid the runtime overhead of the no-op
        # `cast` function call
        node = symbol.node
        if node is not None:
            return node.type  # type: ignore

        return None

    def _paginated_method_callback(
        self, attr_name: str
    ) -> t.Callable[[AttributeContext], Type]:
        def callback(ctx: AttributeContext) -> Type:
            # do not modify the type if the object type is not generic
            if not isinstance(ctx.type, Instance):
                return ctx.default_attr_type
            if len(ctx.type.args) != 1:
                return ctx.default_attr_type
            # do not modify the type when operating on non-callable data
            if not isinstance(ctx.default_attr_type, CallableType):
                return ctx.default_attr_type

            # resolve the client class under which this paginator table was parametrized
            client_class_type = get_proper_type(ctx.type.args[0])

            # now resolve the attribute name against that client class, and if it is not
            # of an expected type (i.e. a callable itself), return the original type
            attr_type = self._get_attribute_type(client_class_type, attr_name)
            if attr_type is None or not isinstance(attr_type, CallableType):
                return ctx.default_attr_type

            # modify the callable type to be a paginated variant
            return attr_type.copy_modified(
                # prepend 'paginated.' to the name
                name=f"paginated.{attr_type.name}",
                # trim the 'self' argument from the arg list
                arg_types=attr_type.arg_types[1:],
                arg_kinds=attr_type.arg_kinds[1:],
                arg_names=attr_type.arg_names[1:],
                # return type is a paginator
                ret_type=self._get_paginator_type(),
            )

        return callback

    def get_attribute_hook(
        self, fullname: str
    ) -> t.Optional[t.Callable[[AttributeContext], Type]]:
        if fullname.startswith(PAGINATOR_TABLE_NAME):
            attr_name = fullname.split(".")[-1]
            return self._paginated_method_callback(attr_name)
        return None


def plugin(version: str) -> t.Type[Plugin]:
    return GlobusSDKPlugin
