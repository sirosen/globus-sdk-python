import enum
import typing as t
from collections import deque


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


class ScopeGraph:
    def __init__(self):
        self.top_level_scopes: t.Set[str] = set()
        self.nodes: t.Set[str] = set()
        self.edges: t.Set[t.Tuple[str, str, bool]] = set()

    @property
    def dependencies(self):
        return self.edges

    def add_edge(self, src: str, dest: str, optional: bool) -> None:
        self.edges.add((src, dest, optional))

    def __str__(self) -> str:
        lines = ["digraph scopes {", '  rankdir="LR";', ""]
        for node in self.top_level_scopes:
            lines.append("  " + node)
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


def _convert_trees(trees: t.List[ScopeTreeNode]) -> ScopeGraph:
    graph = ScopeGraph()
    node_queue: t.Deque[ScopeTreeNode] = deque()

    for tree_node in trees:
        node_queue.append(tree_node)
        graph.top_level_scopes.add(tree_node.scope_string)

    while node_queue:
        tree_node = node_queue.pop()
        scope_string = tree_node.scope_string
        graph.nodes.add(scope_string)
        for dep in tree_node.dependencies:
            node_queue.append(dep)
            graph.add_edge(scope_string, dep.scope_string, dep.optional)

    return graph


def parse(scopes: str) -> ScopeGraph:
    trees = ScopeTreeNode.parse(scopes)
    return _convert_trees(trees)


if __name__ == "__main__":
    import sys

    graph = parse(sys.argv[1])
    print("top level scopes:", ", ".join(graph.top_level_scopes))
    print(graph)
