"""
Tooling for an extremely simple lazy-import system, based on inspection of
pyi files.

Given a base module name (used for lookup and error messages) and the name
of a pyi file, we can use the pyi file to lookup import locations.

i.e. Given

  foo.py
  foo.pyi
  bar.py

then if `foo.pyi` has an import `from .bar import BarType`, it is possible to
*read* `foo.pyi` at runtime and use that information to load
`BarType` from `bar`.
"""

from __future__ import annotations

import ast
import sys
import typing as t


def load_all_tuple(modname: str, pyi_filename: str) -> tuple[str, ...]:
    """
    Load the __all__ tuple from a ``.pyi`` file.

    This should run before the getattr and dir implementations are defined, as those use
    the runtime ``__all__`` tuple.

    :param modname: The name of the module doing the load. Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    """
    pyi_ast = _parse_pyi(modname, pyi_filename)
    return tuple(_extract_all_tuple_names(modname, pyi_filename, pyi_ast))


def default_getattr_implementation(
    modname: str, pyi_filename: str
) -> t.Callable[[str], t.Any]:
    """
    Build an implementation of module ``__getattr__`` given the module name and
    the pyi file which will drive lazy imports.

    :param modname: The name of the module where ``__getattr__`` is being added.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    """
    module_object = sys.modules[modname]
    all_tuple = module_object.__all__

    def getattr_implementation(name: str) -> t.Any:
        if name in all_tuple:
            value = load_attr(modname, pyi_filename, name)
            setattr(module_object, name, value)
            return value

        raise AttributeError(f"module {modname} has no attribute {name}")

    return getattr_implementation


def default_dir_implementation(modname: str) -> t.Callable[[], list[str]]:
    """
    Build an implementation of module ``__dir__`` given the module name.

    :param modname: The name of the module where ``__dir__`` is being added.
        Usually ``__name__``.
    """
    # dir(globus_sdk) should include everything exported in __all__
    # as well as some explicitly selected attributes from the default dir() output
    # on a module
    #
    # see also:
    # https://discuss.python.org/t/how-to-properly-extend-standard-dir-search-with-module-level-dir/4202
    module_object = sys.modules[modname]
    all_tuple = module_object.__all__

    def dir_implementation() -> list[str]:
        return list(all_tuple) + [
            # __all__ itself can be inspected
            "__all__",
            # useful to figure out where a package is installed
            "__file__",
            "__path__",
        ]

    return dir_implementation


def load_attr(modname: str, pyi_filename: str, attrname: str) -> t.Any:
    """
    Execute an import of a single attribute in the manner that it was declared in a
    ``.pyi`` file.

    The import in the pyi data is expected to be a `from x import y` statement.
    Only the specific attribute will be imported, even if the pyi declares multiple
    imports from the same module.

    :param modname: The name of the module importing the attribute.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    :param attrname: The name of the attribute to load.
    """
    import importlib

    attr_source = find_source_module(modname, pyi_filename, attrname)
    attr_source_mod = importlib.import_module(attr_source, modname)
    return getattr(attr_source_mod, attrname)


def find_source_module(modname: str, pyi_filename: str, attrname: str) -> str:
    """
    Find the source module which provides an attribute, based on a declared import in a
    ``.pyi`` file.

    The ``.pyi`` data will be parsed as AST and scanned for an appropriate import.

    :param modname: The name of the module importing the attribute.
        Usually ``__name__``.
    :param pyi_filename: The name of the ``pyi`` file relative to ``modname``.
        ``importlib.resources`` will use both of these fields to load the ``pyi``
        data, so the file must be in package metadata.
    :param attrname: The name of the attribute to load.
    """
    pyi_ast = _parse_pyi(modname, pyi_filename)
    import_from = _find_import_from(modname, pyi_ast, attrname)
    # type ignore the possibility of 'import_from.module == None'
    # as it's not possible from parsed code
    return ("." * import_from.level) + import_from.module  # type: ignore[operator]


def _find_import_from(
    modname: str, pyi_ast: ast.Module, attrname: str
) -> ast.ImportFrom:
    for statement in pyi_ast.body:
        if not isinstance(statement, ast.ImportFrom):
            continue

        if attrname in [alias.name for alias in statement.names]:
            return statement

    raise LookupError(f"Could not find import of '{attrname}' in '{modname}'.")


def _parse_pyi(anchor_module_name: str, pyi_filename: str) -> ast.Module:
    import importlib.resources

    if (anchor_module_name, pyi_filename) not in _parsed_module_cache:
        if sys.version_info >= (3, 9):
            source = (
                importlib.resources.files(anchor_module_name)
                .joinpath(pyi_filename)
                .read_bytes()
            )
        else:
            source = importlib.resources.read_binary(anchor_module_name, pyi_filename)
        _parsed_module_cache[(anchor_module_name, pyi_filename)] = ast.parse(source)
    return _parsed_module_cache[(anchor_module_name, pyi_filename)]


_parsed_module_cache: dict[tuple[str, str], ast.Module] = {}


def _extract_all_tuple_names(
    modname: str, pyi_filename: str, pyi_ast: ast.Module
) -> t.Iterator[str]:
    all_value = _find_all_value(modname, pyi_filename, pyi_ast)
    for element in all_value.elts:
        if not isinstance(element, ast.Constant):
            continue
        yield element.value


def _find_all_value(modname: str, pyi_filename: str, pyi_ast: ast.Module) -> ast.Tuple:
    for statement in pyi_ast.body:
        if not isinstance(statement, ast.Assign):
            continue
        if len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id != "__all__":
            continue
        if not isinstance(statement.value, ast.Tuple):
            break
        return statement.value
    raise LookupError(
        f"Could not load '__all__' tuple from '{pyi_filename}' for '{modname}'."
    )
