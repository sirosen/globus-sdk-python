#!/usr/bin/env python
"""
This script is meant to be a standalone tool which can build an sdist, then
extract the `python_requires` bound from that `sdist` and print it to stdout.

It should use pure, stdlib python *on invocation*.
However, it will create and reuse a virtualenv to install `build`, and then
rely on `python -m build --sdist`.

Assumes that you are running from the root of the project, where
`python -m build` will be able to find package data.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import platform
import subprocess
import tarfile
import tempfile
import venv

parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("-v", "--verbose", action="store_true", default=False)
parser.add_argument(
    "-m",
    "--mode",
    default="lower-bound",
    choices=["lower-bound", "full"],
    help="How to output the python_requires data. "
    "The default ('lower-bound') mode will print only the lower bound version number.",
)
args = parser.parse_args()

if platform.system() == "Windows":
    win_cache_dir = os.getenv("LOCALAPPDATA", os.getenv("APPDATA"))
    assert win_cache_dir, "cannot find APPDATA dir, cannot cache, abort!"
    cache_dir = pathlib.Path(win_cache_dir)
else:
    cache_dir = pathlib.Path.home() / ".cache"

VENV_CACHE_DIR = cache_dir / "get_python_requires"
VENV_CACHE_DIR.mkdir(exist_ok=True)

BUILD_VENV = VENV_CACHE_DIR / "venv-build"
BUILD_PYTHON = str(BUILD_VENV / "bin" / "python")
if BUILD_VENV.exists():
    if args.verbose:
        print(f"Reusing existing venv at {BUILD_VENV}")
else:
    if args.verbose:
        print(f"Creating build venv at {BUILD_VENV}")
    venv.create(str(BUILD_VENV), with_pip=True)
    subprocess.run(
        [BUILD_PYTHON, "-m", "pip", "install", "build"], check=True, capture_output=True
    )

# now the venv exists and has build, so build!
# but do it all careful-like, to a tmpdir and capturing output
if args.verbose:
    print("Invoking 'python -m build' to produce a temporary sdist")
with tempfile.TemporaryDirectory() as tmpdir:
    subprocess.run(
        [BUILD_PYTHON, "-m", "build", "--sdist", "-o", tmpdir],
        check=True,
        capture_output=True,
    )

    # now we have an sdist, so let's find it.
    # the package version will be in the name, so we sniff for any .tar.gz file
    # there will only be one file
    sdist_path = next(pathlib.Path(tmpdir).glob("*.tar.gz"))
    dist_name = sdist_path.name.rsplit(".", 2)[0]
    with tarfile.open(sdist_path, "r:gz") as tf:
        try:
            pkg_info = tf.extractfile(f"{dist_name}/PKG-INFO").read().decode()
        except Exception:
            raise RuntimeError("Could not find and read PKG-INFO in sdist")
    try:
        requires_python_line = [
            line
            for line in pkg_info.splitlines()
            if line.startswith("Requires-Python:")
        ][0]
    except IndexError:
        raise RuntimeError("Could not find 'Requires-Python' in PKG-INFO")
    requires_python = requires_python_line.partition(":")[2].strip()


def find_lower_bound(req):
    reqs = req.split(",")
    lower_bounds = []
    for r in reqs:
        if r.startswith(">="):
            lower_bounds.append(r[2:])
        elif r.startswith(">"):
            raise RuntimeError(
                "Found a > requirement, rejecting as invalid (use '>=' instead)"
            )
    if len(lower_bounds) > 1:
        raise RuntimeError("Found multiple lower bounds, cannot choose one")
    elif len(lower_bounds) == 0:
        raise RuntimeError("Found no lower bounds")
    else:
        return lower_bounds[0]


if args.mode == "full":
    print(requires_python)
elif args.mode == "lower-bound":
    lower_bound = find_lower_bound(requires_python)
    print(lower_bound)
else:
    raise NotImplementedError(f"Unknown mode {args.mode}")
