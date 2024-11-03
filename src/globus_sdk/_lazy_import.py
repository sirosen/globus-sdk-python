"""
Tooling for an extremely simple lazy-import system, based on inspection of
FromImports in an `if t.TYPE_CHECKING` branch.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
import typing as t


def load_attr(modname: str, attrname: str) -> t.Any:
    mod_ast = _parse_module(modname)
    attr_source = find_source_module(modname, attrname, mod_ast=mod_ast)
    attr_source_mod = importlib.import_module(attr_source, modname)
    return getattr(attr_source_mod, attrname)


def find_source_module(
    modname: str, attrname: str, mod_ast: ast.Module | None = None
) -> str:
    if mod_ast is None:
        mod_ast = _parse_module(modname)
    import_from = find_type_checking_import_from(modname, mod_ast, attrname)
    # type ignore the possibility of 'import_from.module == None'
    # as it's not possible from parsed code
    return ("." * import_from.level) + import_from.module  # type: ignore[operator]


def _parse_module(modname: str) -> ast.Module:
    if modname not in _parsed_module_cache:
        mod = sys.modules[modname]
        source = inspect.getsource(mod)
        _parsed_module_cache[modname] = ast.parse(source)
    return _parsed_module_cache[modname]


_parsed_module_cache: dict[str, ast.Module] = {}


def find_type_checking_import_from(
    modname: str, mod_ast: ast.Module, attrname: str
) -> ast.ImportFrom:
    if_clause = _find_type_checking_if(modname, mod_ast)
    if_body = if_clause.body
    for statement in if_body:
        if not isinstance(statement, ast.ImportFrom):
            continue

        if attrname in [alias.name for alias in statement.names]:
            return statement

    raise LookupError(f"Could not find import of '{attrname}' in '{modname}'.")


def _find_type_checking_if(modname: str, mod_ast: ast.Module) -> ast.If:
    if modname in _type_checking_if_cache:
        return _type_checking_if_cache[modname]

    for statement in mod_ast.body:
        if not isinstance(statement, ast.If):
            continue
        if not isinstance(statement.test, ast.Attribute):
            continue

        attr_node: ast.Attribute = statement.test
        if not isinstance(attr_node.value, ast.Name):
            continue
        name_node: ast.Name = attr_node.value
        if name_node.id == "t" and attr_node.attr == "TYPE_CHECKING":
            _type_checking_if_cache[modname] = statement
            return statement

    raise LookupError("Could not find 'TYPE_CHECKING' branch in '{modname}'.")


_type_checking_if_cache: dict[str, ast.If] = {}
