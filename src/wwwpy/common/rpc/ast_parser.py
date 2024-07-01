from __future__ import annotations
import ast
import importlib.util
from typing import NamedTuple, List


class Function(NamedTuple):
    name: str


class Module:
    def __init__(self, name: str, functions: List[Function]):
        self.name = name

        self.functions: List[Function] = functions
        self._funcs = {f.name: f for f in self.functions}

    def __getitem__(self, name) -> Function:
        return self._funcs.get(name, None)


def module_from_package_name(package_name: str) -> Module | None:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return None

    # return spec.origin if spec else None
    source_code = spec.loader.get_source(package_name)
    functions = _get_function_definitions(source_code)
    return Module(package_name, functions)


def _get_function_definitions(source_code) -> List[Function]:
    tree = ast.parse(source_code)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_name = node.name
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                arg_annotation = ast.get_source_segment(source_code, arg.annotation) if arg.annotation else None
                args.append(f"{arg_name}: {arg_annotation}" if arg_annotation else arg_name)

            returns = ast.get_source_segment(source_code, node.returns) if node.returns else None
            signature = f"def {function_name}({', '.join(args)}) -> {returns}" if returns else f"def {function_name}({', '.join(args)})"
            f = Function(function_name)
            functions.append(f)

    return functions
