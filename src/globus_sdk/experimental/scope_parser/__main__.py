import sys
import timeit
import warnings

from ._parser import parse_scope_graph

warnings.warn(
    "This is a test module for scope parsing. It is not intended for public use.",
    stacklevel=1,
)


def timeit_test() -> None:
    for scope_depth, num_iterations in (
        (10, 1000),
        (100, 1000),
        (1000, 1000),
        (2000, 100),
        (3000, 100),
        (4000, 100),
        (5000, 100),
    ):
        setup = f"""\
from globus_sdk.experimental.scope_parser import Scope
big_scope = ""
for i in range({scope_depth}):
    big_scope += f"foo{{i}}["
big_scope += "bar"
for _ in range({scope_depth}):
    big_scope += "]"
"""

        time_taken = timeit.timeit(
            "Scope.deserialize(big_scope)", setup=setup, number=num_iterations
        )
        average = time_taken / num_iterations
        print(f"{num_iterations} runs, {scope_depth} depth, avg time taken: {average}")


def parse_test(scope_string: str) -> None:
    parsed_graph = parse_scope_graph(sys.argv[1])
    print(
        "top level scopes:",
        ", ".join([name for name, _optional in parsed_graph.top_level_scopes]),
    )
    print(parsed_graph)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("This script supports two usage patterns:")
        print("    python -m globus_sdk.experimental.scope_parser SCOPE_STRING")
        print("    python -m globus_sdk.experimental.scope_parser --timeit")
        sys.exit(0)

    if sys.argv[1] == "--timeit":
        timeit_test()
    else:
        parse_test(sys.argv[1])


main()
