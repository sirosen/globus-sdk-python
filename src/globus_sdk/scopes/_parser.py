import enum
import typing as t


class ScopeParseError(ValueError):
    pass


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


def _tokenize(scope_string: str) -> t.List[ParseToken]:
    tokens: t.List[ParseToken] = []
    current_token: t.List[str] = []
    for idx, c in enumerate(scope_string):
        try:
            peek: t.Optional[str] = scope_string[idx + 1]
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


def _parse_tokens(tokens: t.List[ParseToken]) -> t.List["ScopeTreeNode"]:
    # value to return
    ret: t.List[ScopeTreeNode] = []
    # track whether or not the current scope is optional (has a preceding *)
    current_optional = False
    # keep a stack of "parents", each time we enter a `[` context, push the last scope
    # and each time we exit via a `]`, pop from the stack
    parents: t.List[ScopeTreeNode] = []
    # track the current (or, by similar terminology, "last") complete scope seen
    current_scope: t.Optional[ScopeTreeNode] = None

    for idx in range(len(tokens)):
        token = tokens[idx]
        try:
            peek: t.Optional[ParseToken] = tokens[idx + 1]
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
                parents[-1].dependencies.append(current_scope)
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
        self.dependencies: t.List[ScopeTreeNode] = []

    def add_dependency(self, subtree: "ScopeTreeNode") -> None:
        self.dependencies.append(subtree)

    def __repr__(self) -> str:
        parts: t.List[str] = [f"'{self.scope_string}'"]
        if self.optional:
            parts.append("optional=True")
        if self.dependencies:
            parts.append(f"dependencies={self.dependencies!r}")
        return "ScopeTreeNode(" + ", ".join(parts) + ")"

    @staticmethod
    def parse(scope_string: str) -> t.List["ScopeTreeNode"]:
        tokens = _tokenize(scope_string)
        return _parse_tokens(tokens)


class ScopeGraphNode:
    def __init__(
        self,
        scope_string: str,
    ) -> None:
        self.scope_string = scope_string
        self.edges: t.List[t.Tuple[ScopeGraphNode, bool]] = []

    @property
    def dependencies(self):
        return self.edges

    def add_edge(self, dest: "ScopeGraphNode", optional: bool) -> None:
        if (dest, optional) not in self.edges:
            self.edges.append((dest, optional))

    def __str__(self) -> str:
        return self.scope_string


def _convert_trees(
    trees: t.List[ScopeTreeNode],
) -> t.Tuple[t.List[str], t.List[ScopeGraphNode]]:
    name_to_node_map: t.Dict[str, ScopeGraphNode] = {}

    # populate the map with values, but don't draw any edges yet
    node_queue = list(trees)
    for tree_node in node_queue:
        scope_string = tree_node.scope_string
        if scope_string not in name_to_node_map:
            name_to_node_map[scope_string] = ScopeGraphNode(scope_string)
        for dep in tree_node.dependencies:
            node_queue.append(dep)

    # having done that, reset and populate the edges in a second BFS traversal
    node_queue = list(trees)
    for tree_node in node_queue:
        scope_string = tree_node.scope_string
        graph_node = name_to_node_map[scope_string]
        for dep in tree_node.dependencies:
            node_queue.append(dep)
            graph_node_dep = name_to_node_map[dep.scope_string]
            graph_node.add_edge(graph_node_dep, dep.optional)

    return ([t.scope_string for t in trees], list(name_to_node_map.values()))


def parse(scopes: str) -> t.Tuple[t.Set[str], t.Set["ScopeGraphNode"]]:
    trees = ScopeTreeNode.parse(scopes)
    top_level_scopes, graph_nodes = _convert_trees(trees)
    return set(top_level_scopes), set(graph_nodes)


def graph_to_dot(nodes: t.Set[ScopeGraphNode]) -> str:
    lines = ["digraph scopes {", '  rankdir="LR";', ""]
    for node in nodes:
        for target, optional in node.edges:
            target_str = str(target)
            if optional:
                target_str += ' [ label = "optional" ]'
            lines.append(f"  {node} -> {target_str};")
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    top_level_scopes, graph = parse(sys.argv[1])
    print("top level scopes:", ", ".join(top_level_scopes))
    print(graph_to_dot(graph))
