import importlib
from wwwpy.common.rpc.func_registry import FuncMeta


class Invoker:
    def __init__(self, module: FuncMeta):
        self.module = module
        self.module_type = _load_package(module.name)

    def __getitem__(self, item):
        return _Invocable(getattr(self.module_type, item))


class _Invocable:
    def __init__(self, func):
        self.func = func


def _load_package(package_name: str):
    try:
        return importlib.import_module(package_name)
    except ImportError:
        print(f"Package '{package_name}' could not be loaded.")
        return None
