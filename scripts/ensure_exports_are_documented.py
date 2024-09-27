#!/usr/bin/env python
from __future__ import annotations

import functools
import glob
import os
import pathlib
import re
import sys
import typing as t

REPO_ROOT = pathlib.Path(__file__).parent.parent

_ALL_NAME_PATTERN = re.compile(r'\s+"(\w+)",?')

PACKAGE_DIRS_TO_SCAN = (
    "globus_sdk",
    "globus_sdk/scopes",
)

DEPRECATED_NAMES = {
    "TimerAPIError",
    "TimerClient",
    "TimerScopes",
}


def load_docs() -> dict[str, str]:
    all_docs = {}
    for file in glob.glob("docs/**/*.rst", recursive=True):
        with open(file) as f:
            all_docs[file] = f.read()
    return all_docs


def iter_all_documented_names() -> t.Iterable[str]:
    # names under these directives
    #
    #   .. autoclass:: <name>
    #   .. autofunction:: <name>
    #   .. autoexception:: <name>
    #   .. autodata:: <name>
    autodoc_pattern = re.compile(
        r"^\.\.\s+auto(?:class|function|exception|data)\:\:\s+(?:\w+\.)*(\w+)$",
        flags=re.MULTILINE,
    )
    # names under these directives
    #
    #   .. class:: <name>
    #   .. py:data:: <name>
    pydoc_pattern = re.compile(
        r"^\.\.\s+(?:py\:data|class)\:\:\s+(?:\w+\.)*(\w+)$",
        flags=re.MULTILINE,
    )
    for data in load_docs().values():
        for match in autodoc_pattern.finditer(data):
            yield match.group(1)
        for match in pydoc_pattern.finditer(data):
            yield match.group(1)


@functools.lru_cache
def all_documented_names() -> frozenset[str]:
    return frozenset(iter_all_documented_names())


def is_documented(name: str) -> bool:
    return name in all_documented_names()


def get_names_from_all_list(package_dir) -> list[str]:
    with open(f"src/{package_dir}/__init__.py") as fp:
        contents = fp.readlines()

    names: list[str] = []
    found_all = False
    for line in contents:
        if found_all:
            if line.strip() == ")":
                break
            names.append(_ALL_NAME_PATTERN.match(line).group(1))
        else:
            if line.strip() == "__all__ = (":
                found_all = True
            else:
                continue
    return [n for n in names if not n.startswith("_")]


def ensure_exports_are_documented() -> bool:
    success = True
    used_deprecations = set()
    for package_dir in PACKAGE_DIRS_TO_SCAN:
        for name in get_names_from_all_list(package_dir):
            if name in DEPRECATED_NAMES:
                used_deprecations.add(name)
                continue
            if not is_documented(name):
                print(
                    f"'src/{package_dir}/__init__.py::{name}' "
                    "was not found in doc directives"
                )
                success = False
    if unused_deprecations := (DEPRECATED_NAMES - used_deprecations):
        print(f"unused deprecations: {unused_deprecations}")
        success = False
    return success


if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    if not ensure_exports_are_documented():
        exit(1)
    sys.exit(0)
