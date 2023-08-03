from __future__ import annotations

import sys
import timeit
import warnings

from ._parser import parse_scope_graph

warnings.warn(
    "This is a test module for scope parsing. It is not intended for public use.",
    stacklevel=1,
)


def timeit_test() -> None:
    for size, num_iterations, style in (
        (10, 1000, "deep"),
        (100, 1000, "deep"),
        (1000, 1000, "deep"),
        (2000, 100, "deep"),
        (3000, 100, "deep"),
        (4000, 100, "deep"),
        (5000, 100, "deep"),
        (5000, 1000, "wide"),
        (10000, 1000, "wide"),
    ):
        if style == "deep":
            setup = f"""\
from globus_sdk.experimental.scope_parser import Scope
big_scope = ""
for i in range({size}):
    big_scope += f"foo{{i}}["
big_scope += "bar"
for _ in range({size}):
    big_scope += "]"
"""
        elif style == "wide":
            setup = f"""\
from globus_sdk.experimental.scope_parser import Scope
big_scope = ""
for i in range({size}):
    big_scope += f"foo{{i}} "
"""
        else:
            raise NotImplementedError

        timer = timeit.Timer("Scope.parse(big_scope)", setup=setup)

        raw_timings = timer.repeat(repeat=5, number=num_iterations)
        best, worst, average, variance = _stats(raw_timings)
        if style == "deep":
            print(f"{num_iterations} runs on a deep scope, depth={size}")
        elif style == "wide":
            print(f"{num_iterations} runs on a wide scope, width={size}")
        else:
            raise NotImplementedError
        print(f"  best={best} worst={worst} average={average} variance={variance}")
        print(f"  normalized best={best / num_iterations}")
        print()
    print("The most informative stat over these timings is the min timing (best).")
    print("Normed best is best/iterations.")
    print(
        "Max timing (worst) and dispersion (variance vis-a-vis average) indicate "
        "how consistent the results are, but are not a report of speed."
    )


def _stats(timing_data: list[float]) -> tuple[float, float, float, float]:
    best = min(timing_data)
    worst = max(timing_data)
    average = sum(timing_data) / len(timing_data)
    variance = sum((x - average) ** 2 for x in timing_data) / len(timing_data)
    return best, worst, average, variance


def parse_test(scope_string: str) -> None:
    parsed_graph = parse_scope_graph(scope_string)
    print(
        "top level scopes:",
        ", ".join([name for name, _optional in parsed_graph.top_level_scopes]),
    )
    print(parsed_graph)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("This script supports two usage patterns:")
        print("    python -m globus_sdk.experimental.scope_parser SCOPE_STRING")
        print("    python -m globus_sdk.experimental.scope_parser --timeit")
        sys.exit(0)

    print()
    if sys.argv[1] == "--timeit":
        timeit_test()
    else:
        parse_test(sys.argv[1])


main()
