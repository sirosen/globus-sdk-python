#!/usr/bin/env python
"""
This script wraps `pip-compile` in a way similar to `pip-compile-multi` but with a few
tweaks/simplifications which are more appropriate to our usage.

1. Run pip-compile independently for each X.in -> X.txt
   (pip-compile-multi cross-correlates between files)
2. Set CUSTOM_COMPILE_COMMAND (pip-compile-multi does not support this)
3. Target a directory named by the current python minor version

Equivalently, we could write out `pip-compile <options> <source> -o <dest>` in our
tox.ini as the commands list.
This wrapper is just a minor convenience.
"""
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
REQS_DIR = REPO_ROOT / "requirements"

PY_MAJOR_MINOR = f"{sys.version_info[0]}.{sys.version_info[1]}"


def main():
    subdir = REQS_DIR / f"py{PY_MAJOR_MINOR}"
    subdir.mkdir(exist_ok=True)

    reqs_in_files = REQS_DIR.glob("*.in")
    print(f'running pip-compile on "{REQS_DIR}/*.in"')
    for absolute_source in reqs_in_files:
        source = absolute_source.relative_to(REQS_DIR)
        dest = (subdir / source).with_suffix(".txt").relative_to(REQS_DIR)
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
