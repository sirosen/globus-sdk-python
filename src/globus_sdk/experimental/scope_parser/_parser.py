from __future__ import annotations

import enum
import typing as t
from collections import defaultdict, deque

from .errors import ScopeCycleError, ScopeParseError


class ParseTokenType(enum.Enum):
    # a string like 'urn:globus:auth:scopes:transfer.api.globus.org:all'
    scope_string = enum.auto()
    # the optional marker, '*'
    opt_marker = enum.auto()
    # '[' and ']'
    lbracket = enum.auto()
    rbracket = enum.auto()


class ParseToken:
    def __init__(self, value: str, token_type: ParseTokenType) -> None:
        self.value = value
        self.token_type = token_type


def _tokenize(scope_string: str) -> list[ParseToken]:
    tokens: list[ParseToken] = []
    current_token: list[str] = []
    for idx, c in enumerate(scope_string):
        try:
            peek: str | None = scope_string[idx + 1]
        except IndexError:
            peek = None

        if c in "[]* ":
            if current_token:
                tokens.append(
                    ParseToken("".join(current_token), ParseTokenType.scope_string)
                )
                current_token = []

            if c == "*":
                if peek == " ":
                    raise ScopeParseError("'*' must not be followed by a space")
                tokens.append(ParseToken(c, ParseTokenType.opt_marker))
            elif c == "[":
                tokens.append(ParseToken(c, ParseTokenType.lbracket))
            elif c == "]":
                if peek is not None and peek not in (" ", "]"):
                    raise ScopeParseError("']' may only be followed by a space or ']'")
                tokens.append(ParseToken(c, ParseTokenType.rbracket))
            elif c == " ":
                if peek == "[":
                    raise ScopeParseError("'[' cannot have a preceding space")
            else:
                raise NotImplementedError
        else:
            current_token.append(c)
    if current_token:
        tokens.append(ParseToken("".join(current_token), ParseTokenType.scope_string))
    return tokens


def _parse_tokens(tokens: list[ParseToken]) -> list[ScopeTreeNode]:
    # value to return
    ret: list[ScopeTreeNode] = []
    # track whether or not the current scope is optional (has a preceding *)
    current_optional = False
    # keep a stack of "parents", each time we enter a `[` context, push the last scope
    # and each time we exit via a `]`, pop from the stack
    parents: list[ScopeTreeNode] = []
    # track the current (or, by similar terminology, "last") complete scope seen
    current_scope: ScopeTreeNode | None = None

    for idx in range(len(tokens)):
        token = tokens[idx]
        try:
            peek: ParseToken | None = tokens[idx + 1]
        except IndexError:
            peek = None

        if token.token_type == ParseTokenType.opt_marker:
            current_optional = True
            if peek is None:
                raise ScopeParseError("ended in optional marker")
            if peek.token_type != ParseTokenType.scope_string:
                raise ScopeParseError(
                    "a scope string must always follow an optional marker"
                )

        elif token.token_type == ParseTokenType.lbracket:
            if peek is None:
                raise ScopeParseError("ended in left bracket")
            if peek.token_type == ParseTokenType.rbracket:
                raise ScopeParseError("found empty brackets")
            if peek.token_type == ParseTokenType.lbracket:
                raise ScopeParseError("found double left-bracket")
            if not current_scope:
                raise ScopeParseError("found '[' without a preceding scope string")

            parents.append(current_scope)
        elif token.token_type == ParseTokenType.rbracket:
            if not parents:
                raise ScopeParseError("found ']' with no matching '[' preceding it")
            parents.pop()
        else:
            current_scope = ScopeTreeNode(token.value, optional=current_optional)
            current_optional = False
            if parents:
                parents[-1].add_dependency(current_scope)
            else:
                ret.append(current_scope)
    if parents:
        raise ScopeParseError("unclosed brackets, missing ']'")

    return ret


class ScopeTreeNode:
    """
    This is an intermediate representation for scope parsing.
    """

    def __init__(
        self,
        scope_string: str,
        *,
        optional: bool,
    ) -> None:
        self.scope_string = scope_string
        self.optional = optional
        self.dependencies: list[ScopeTreeNode] = []

    def add_dependency(self, subtree: ScopeTreeNode) -> None:
        self.dependencies.append(subtree)

    def __repr__(self) -> str:
        parts: list[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "ScopeTreeNode(" + ", ".join(parts) + ")"

    @staticmethod
    def parse(scope_string: str) -> list[ScopeTreeNode]:
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)


class ScopeGraph:
    def __init__(self) -> None:
        self.top_level_scopes: set[tuple[str, bool]] = set()
        self.nodes: set[str] = set()
        self.edges: set[tuple[str, str, bool]] = set()
        self._nodes_to_outbound_edges: dict[
            str, set[tuple[str, str, bool]]
        ] = defaultdict(set)

    def get_child_edges(self, node: str) -> set[tuple[str, str, bool]]:
        return set(self._nodes_to_outbound_edges[node])

    def add_edge(self, src: str, dest: str, optional: bool) -> None:
        self.edges.add((src, dest, optional))
        self._nodes_to_outbound_edges[src].add((src, dest, optional))

    def _normalize_optionals(self) -> None:
        to_remove: set[tuple[str, str, bool]] = set()
        for edge in self.edges:
            src, dest, optional = edge
            if not optional:
                continue
            alter_ego = (src, dest, not optional)
            if alter_ego in self.edges:
                to_remove.add(edge)
        self.edges = self.edges - to_remove
        for edge in to_remove:
            src, _, _ = edge
            self._nodes_to_outbound_edges[src].remove(edge)

    def _check_cycles(self) -> None:
        # check for two invariants:
        # 1. no strongly connected components of size > 1
        # 2. no self-loops
        #
        # for (1) we use Tarjan's algorithm
        # thorough comments for the algorithm follow because it is subtle and nontrivial
        # however, we do not seek to explain *why* the algorithm works here
        #
        # see also:
        #   Wikipedia
        #   https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
        #
        #   Original Paper (1972)
        #     https://citeseerx.ist.psu.edu/doc/10.1.1.327.8418
        #
        # the following four variables are for Tarjan's
        # - index: the index of the current node
        # - stack: a stack of nodes
        # - node_indices: a map from each node to its index, an incrementing integer
        #   which is assigned to each node as it is discovered
        # - node_lowlink: a map from each node to its lowlink, the smallest index of any
        #   node reachable from this node on the stack
        index = 0
        stack: list[str] = []
        node_indices: dict[str, int] = {}
        node_lowlink: dict[str, int] = {}

        # the strongconnect method yields strongly connected components (as an iterator)
        def strongconnect(node: str) -> t.Iterator[list[str]]:
            nonlocal index
            nonlocal stack
            node_indices[node] = index
            node_lowlink[node] = index
            index += 1
            stack.append(node)

            # for all children of the current node...
            for _, dest, _ in self.get_child_edges(node):
                # if the child has not been visited, visit it (recursively)
                # effectively, this proceeds down a DFS incrementing the index
                # assigned to newly discovered nodes
                if dest not in node_indices:
                    yield from strongconnect(dest)
                    # after uncovering the strongly connected components which are
                    # reachable from the dest, update the lowlink of the current node
                    # if dest found a lower lowlink
                    # this would indicate that dest or its descendants point back "up"
                    # the stack to 'node' or one of its ancestors
                    node_lowlink[node] = min(node_lowlink[node], node_lowlink[dest])
                # otherwise, but only if dest is on the stack, update the lowlink of
                # 'node' if necessary
                if dest in stack:
                    node_lowlink[node] = min(node_lowlink[node], node_indices[dest])

            # if the current node was discovered to be a root node (because it was not
            # connected to any node with a lower index) then pop the stack until we
            # reach the current node, and that will be a strongly connected component
            if node_lowlink[node] == node_indices[node]:
                component: list[str] = []
                while stack[-1] != node:
                    top = stack.pop()
                    component.append(top)
                component.append(stack.pop())
                yield component

        # first, check for self-loops to eliminate this case
        for src, dest, _ in self.edges:
            if src == dest:
                raise ScopeCycleError(f"A self-loop was detected: {src}->{dest}")

        # now, detect strongly connected components
        components: list[list[str]] = []
        for node in self.nodes:
            if node in node_indices:
                continue
            components.extend(strongconnect(node))

        for component in components:
            if len(component) > 1:
                raise ScopeCycleError(f"A cycle was detected: {component}")

    def __str__(self) -> str:
        lines = ["digraph scopes {", '  rankdir="LR";', ""]
        for node, optional in self.top_level_scopes:
            lines.append(f"  {'*' if optional else ''}{node}")
        lines.append("")

        # do two passes to put all non-optional edges first
        for source, dest, optional in self.edges:
            if optional:
                continue
            lines.append(f"  {source} -> {dest};")
        for source, dest, optional in self.edges:
            if not optional:
                continue
            lines.append(f'  {source} -> {dest} [ label = "optional" ];')
        lines.append("")
        lines.append("}")
        return "\n".join(lines)


def _convert_trees(trees: list[ScopeTreeNode]) -> ScopeGraph:
    graph = ScopeGraph()
    node_queue: t.Deque[ScopeTreeNode] = deque()

    for tree_node in trees:
        node_queue.append(tree_node)
        graph.top_level_scopes.add((tree_node.scope_string, tree_node.optional))

    while node_queue:
        tree_node = node_queue.pop()
        scope_string = tree_node.scope_string
        graph.nodes.add(scope_string)
        for dep in tree_node.dependencies:
            node_queue.append(dep)
            graph.add_edge(scope_string, dep.scope_string, dep.optional)

    return graph


def parse_scope_graph(scopes: str) -> ScopeGraph:
    trees = ScopeTreeNode.parse(scopes)
    graph = _convert_trees(trees)
    graph._normalize_optionals()
    graph._check_cycles()
    return graph


if __name__ == "__main__":
    import sys

    parsed_graph = parse_scope_graph(sys.argv[1])
    print(
        "top level scopes:",
        ", ".join([name for name, _optional in parsed_graph.top_level_scopes]),
    )
    print(parsed_graph)
