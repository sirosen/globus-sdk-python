from __future__ import annotations

import typing as t

from .representation import Scope


class StaticScopeCollectionMeta(type):
    """
    The metaclass for StaticScopeCollection.

    This defines the the stringification of these classes.
    """

    def __str__(self) -> str:
        name: str = getattr(self, "__name__", "<unnamed-collection>")
        resource_server: str = getattr(
            self, "resource_server", "<unknown-resource-server>"
        )

        scope_names: t.Iterable[str] = self._scope_names()  # type: ignore[attr-defined]

        return f"{name}[{resource_server}]\n" + "\n".join(
            f"  {name}:\n    {getattr(self, name)}" for name in scope_names
        )


class StaticScopeCollection(metaclass=StaticScopeCollectionMeta):
    """
    A static scope collection is a data container which provides various scopes
    as class attributes.

    ``resource_server`` is available as a class attribute.

    ``str(<class>)`` is well-defined to produce a nice rendering of the scopes
    contained in the class.
    """

    resource_server: t.ClassVar[str]

    @classmethod
    def _scope_names(cls) -> t.Iterator[str]:
        for key, value in vars(cls).items():
            if isinstance(value, Scope):
                yield key


class DynamicScopeCollection:
    """
    The base type for dynamic scope collections, where the resource server is
    variable.

    The class itself is not usable as a collection type, but its instances are.

    The default implementation takes the resource server as the only init-time
    parameter.

    :param resource_server: The resource_server to use for all scopes attached
        to this scope collection.
    """

    # DynamicScopeCollection classes are expected to provide
    # the scope names which they provide as a classvar
    # these are often properties for dynamic computation
    _scope_names: t.ClassVar[tuple[str, ...]]

    def __init__(self, resource_server: str) -> None:
        self.resource_server = resource_server

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.resource_server}]\n" + "\n".join(
            f"  {name}:\n    {getattr(self, name)}" for name in self._scope_names
        )


def _urn_scope(resource_server: str, scope_name: str) -> Scope:
    """
    Convert a short name + resource server string to a scope, in the Globus
    Auth URN format.

    Example Usage:

    >>> _urn_scope("transfer.api.globus.org", "all")
    Scope('urn:globus:auth:scope:transfer.api.globus.org:all')

    :param resource_server: The resource server string.
    :param scope_name: The short name for the scope.
    """
    return Scope(f"urn:globus:auth:scope:{resource_server}:{scope_name}")


def _url_scope(resource_server: str, scope_name: str) -> Scope:
    """
    Convert a short name + resource server string to a scope, in the Globus
    Auth URL format.

    Example Usage:

    >>> _url_scope("actions.globus.org", "hello_world")
    Scope('https://auth.globus.org/scopes/actions.globus.org/hello_world')

    :param resource_server: The resource server string.
    :param scope_name: The short name for the scope.
    """
    return Scope(f"https://auth.globus.org/scopes/{resource_server}/{scope_name}")
