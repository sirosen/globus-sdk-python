from __future__ import annotations

import typing as t
import warnings

from ._parser import parse_scope_graph


class Scope:
    """
    A scope object is a representation of a scope which allows modifications to be
    made. In particular, it supports handling scope dependencies via
    ``add_dependency``.

    `str(Scope(...))` produces a valid scope string for use in various methods.

    :param scope_string: The string which will be used as the basis for this Scope
    :type scope_string: str
    :param optional: The scope may be marked as optional. This means that the scope can
        be declined by the user without declining consent for other scopes
    :type optional: bool
    """

    def __init__(
        self,
        scope_string: str,
        *,
        optional: bool = False,
        dependencies: list[Scope] | None = None,
    ) -> None:
        if any(c in scope_string for c in "[]* "):
            raise ValueError(
                "Scope instances may not contain the special characters '[]* '. "
                "Use either Scope.deserialize or Scope.parse instead"
            )
        self.scope_string = scope_string
        self.optional = optional
        self.dependencies: list[Scope] = [] if dependencies is None else dependencies

    @staticmethod
    def parse(scope_string: str) -> list[Scope]:
        """
        Parse an arbitrary scope string to a list of scopes.

        Zero or more than one scope may be returned, as in the case of an empty string
        or space-delimited scopes.

        .. warning::

            Parsing passes through an intermediary representation which treats scopes
            as a graph. This ensures that the behavior of parses matches the treatment
            of scope strings in Globus Auth authorization flows.
            However, this also means that the parsing does not allow for strings which
            represent consent trees with structures in which the same scope appears in
            multiple parts of the tree.
        """
        scope_graph = parse_scope_graph(scope_string)

        # initialize BFS traversals (one per root node) and copy that data
        # to setup the result data
        bfs_additions: list[Scope] = [
            Scope(s, optional=optional) for s, optional in scope_graph.top_level_scopes
        ]
        results: list[Scope] = list(bfs_additions)

        while bfs_additions:
            current_scope = bfs_additions.pop(0)
            edges = scope_graph.adjacency_matrix[current_scope.scope_string]
            for _, dest, optional in edges:
                dest_scope = Scope(dest, optional=optional)
                current_scope.add_dependency(dest_scope)
                bfs_additions.append(dest_scope)

        return results

    @classmethod
    def deserialize(cls, scope_string: str) -> Scope:
        """
        Deserialize a scope string to a scope object.

        This is the special case of parsing in which exactly one scope must be returned
        by the parse.
        """
        data = Scope.parse(scope_string)
        if len(data) != 1:
            raise ValueError(
                "Deserializing a scope from string did not get exactly one scope. "
                f"Instead got data={data}"
            )
        return data[0]

    def serialize(self) -> str:
        base_scope = ("*" if self.optional else "") + self.scope_string
        if not self.dependencies:
            return base_scope
        return (
            base_scope + "[" + " ".join(c.serialize() for c in self.dependencies) + "]"
        )

    def add_dependency(
        self, scope: str | Scope, *, optional: bool | None = None
    ) -> Scope:
        """
        Add a scope dependency. The dependent scope relationship will be stored in the
        Scope and will be evident in its string representation.

        :param scope: The scope upon which the current scope depends
        :type scope: str
        :param optional: Mark the dependency an optional one. By default it is not. An
            optional scope dependency can be declined by the user without declining
            consent for the primary scope
        :type optional: bool, optional
        """
        if optional is not None:
            if isinstance(scope, Scope):
                raise ValueError(
                    "cannot use optional=... with a Scope object as the argument to "
                    "add_dependency"
                )
            warnings.warn(
                "Passing 'optional' to add_dependency is deprecated. "
                "Construct an optional Scope object instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            scopeobj = Scope(scope, optional=optional)
        else:
            if isinstance(scope, str):
                scopeobj = Scope.deserialize(scope)
            else:
                scopeobj = scope
        self.dependencies.append(scopeobj)
        return self

    def __repr__(self) -> str:
        parts: list[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "Scope(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.serialize()

    def __contains__(self, other: t.Any) -> bool:
        """
        .. warning::

            The ``__contains__`` method is a non-authoritative convenience for comparing
            parsed scopes. Although the essence and intent of the check is summarized
            below, there is no guarantee that it correctly reflects the permissions of a
            token or tokens. The structure of the data for a given consent in Globus
            Auth is not perfectly reflected in the parse tree.

        ``in`` and ``not in`` are defined as permission coverage checks

        ``scope1 in scope2`` means that a token scoped for
        ``scope2`` has all of the permissions of a token scoped for ``scope1``.

        A scope is covered by another scope if

        - the top level strings match
        - the optional-ness matches OR only the covered scope is optional
        - the dependencies of the covered scope are all covered by dependencies of
          the covering scope

        Therefore, the following are true:

        .. code-block:: pycon

            >>> s = lambda x: Scope.deserialize(x)  # define this for brevity below
            # self inclusion works, including when optional
            >>> s("foo") in s("foo")
            >>> s("*foo") in s("*foo")
            # an optional scope is covered by a non-optional one, but not the reverse
            >>> s("*foo") in s("foo")
            >>> s("foo") not in s("*foo")
            # dependencies have the expected meanings
            >>> s("foo") in s("foo[bar]")
            >>> s("foo[bar]") not in s("foo")
            >>> s("foo[bar]") in s("foo[bar[baz]]")
            # dependencies are not transitive and obey "optionalness" matching
            >>> s("foo[bar]") not in s("foo[fizz[bar]]")
            >>> s("foo[bar]") not in s("foo[*bar]")
        """
        # scopes can only contain other scopes
        if not isinstance(other, Scope):
            return False

        # top-level scope must match
        if self.scope_string != other.scope_string:
            return False

        # between self.optional and other.optional, there are four possibilities,
        # of which three are acceptable and one is not
        # both optional and neither optional are okay,
        # 'self' being non-optional and 'other' being optional is okay
        # the failing case is 'other in self' when 'self' is optional and 'other' is not
        #
        #    self.optional | other.optional | (other in self) is possible
        #    --------------|----------------|----------------------------
        #        true      |    true        |    true
        #        false     |    false       |    true
        #        false     |    true        |    true
        #        true      |    false       |    false
        #
        # so only check for that one case
        if self.optional and not other.optional:
            return False

        # dependencies must all be contained -- search for a contrary example
        for other_dep in other.dependencies:
            for dep in self.dependencies:
                if other_dep in dep:
                    break
            # reminder: the else branch of a for-else means that the break was never hit
            else:
                return False

        # all criteria were met -- True!
        return True
