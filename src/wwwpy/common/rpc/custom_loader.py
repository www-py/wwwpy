import importlib
import importlib.abc
import importlib.util
import sys
import ast
from wwwpy.common.rpc import func_registry
from ast import Module, FunctionDef, AsyncFunctionDef, ClassDef


class CustomLoader(importlib.abc.Loader):
    def __init__(self, loader):
        self.loader = loader

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        source = self.loader.get_source(module.__name__)
        proxy_source = func_registry.source_to_proxy(source)
        code = compile(proxy_source, module.__file__, 'exec')
        exec(code, module.__dict__)


class CustomFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname in {'remote', 'remote.rpc'}:
            # Temporarily remove this finder from sys.meta_path to avoid recursion
            orig = sys.meta_path.copy()
            sys.meta_path = [finder for finder in sys.meta_path if not isinstance(finder, CustomFinder)]
            try:
                spec = importlib.util.find_spec(fullname)
            finally:
                # Reinsert this finder back into sys.meta_path
                sys.meta_path = orig

            if spec:
                spec.loader = CustomLoader(spec.loader)
            return spec
        return None
