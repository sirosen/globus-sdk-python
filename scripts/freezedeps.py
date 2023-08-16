#!/usr/bin/env python
"""
This script wraps `pip-compile` in a way similar to `pip-compile-multi` but with a few
tweaks/simplifications which are more appropriate to our usage.

1. Run pip-compile independently for each X.in -> X.txt
   (pip-compile-multi cross-correlates between files)
2. Set CUSTOM_COMPILE_COMMAND (pip-compile-multi does not support this)
3. Use the '--mindeps' flag to control which requirements are compiled

Equivalently, we could write out `pip-compile <options> <source> -o <dest>` in our
tox.ini as the commands list.
This wrapper is just a minor convenience.
"""
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
REQS_DIR = REPO_ROOT / "requirements"

PY_MAJOR_MINOR = f"{sys.version_info[0]}{sys.version_info[1]}"


def main():
    try:
        mindeps = sys.argv[1] == "--mindeps"
    except IndexError:
        mindeps = False

    reqs_in_files = REQS_DIR.glob("*.in")
    print(f'running pip-compile on "{REQS_DIR}/*.in" (mindeps={mindeps})')
    for absolute_source in reqs_in_files:
        # skip if it's a "mindeps" requirement and "mindeps" is not set
        #         or if it's not a "mindeps" requirement and "mindeps" is set
        if ("mindeps" not in absolute_source.name and mindeps) or (
            "mindeps" in absolute_source.name and not mindeps
        ):
            continue
        source = absolute_source.relative_to(REQS_DIR)
        dest = source.with_suffix(".txt")
        print(f"{source} -> {dest}")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "piptools",
                "compile",
                "--strip-extras",
                "-q",
                "--resolver=backtracking",
                str(source),
                "-o",
                str(dest),
                "--upgrade",
            ],
            check=True,
            cwd=REQS_DIR,
            env={"CUSTOM_COMPILE_COMMAND": "tox p -m freezedeps"},
        )


if __name__ == "__main__":
    main()
