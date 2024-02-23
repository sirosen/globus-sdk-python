import glob
import os
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent

_NAME_PAT = re.compile(r'\s+"(\w+)",?')


_DOC_CACHE: dict[str, str] = {}


def load_docs() -> dict[str, str]:
    if _DOC_CACHE:
        return _DOC_CACHE
    for file in glob.glob("docs/**/*.rst", recursive=True):
        with open(file) as f:
            _DOC_CACHE[file] = f.read()
    return _DOC_CACHE


# TODO: is there a better way to test that a name is documented?
# should we check that it appears in a class, autoclass, or similar directive?
def is_documented(name: str) -> bool:
    for data in load_docs().values():
        if name in data:
            return True
    return False


def get_names_from_all_list() -> list[str]:
    with open("src/globus_sdk/__init__.py") as fp:
        contents = fp.readlines()

    names: list[str] = []
    found_all = False
    for line in contents:
        if found_all:
            if line.strip() == ")":
                break
            names.append(_NAME_PAT.match(line).group(1))
        else:
            if line.strip() == "__all__ = (":
                found_all = True
            else:
                continue
    return [n for n in names if not n.startswith("_")]


def ensure_exports_are_documented() -> bool:
    success = True
    for name in get_names_from_all_list():
        if not is_documented(name):
            print(f"{name} is not documented")
            success = False
    return success


if __name__ == "__main__":
    os.chdir(REPO_ROOT)
    if not ensure_exports_are_documented():
        exit(1)
    sys.exit(0)
