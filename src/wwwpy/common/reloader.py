from __future__ import annotations

import inspect
import sys
from pathlib import Path


def reload(module):
    import importlib
    # importlib.invalidate_caches()
    return importlib.reload(module)

def _find_package_location(package_name) -> Path | None:
    import importlib.util

    spec = importlib.util.find_spec(package_name)
    return Path(spec.origin) if spec else None


def unload_path(path: str):
    def accept(module):
        try:
            module_path = inspect.getfile(module)
            return module_path.startswith(path) and module_path != __file__
        except:
            return False

    names = [name for name, module in sys.modules.items() if accept(module)]

    for name in names:
        print(f'Deleting {name}...')
        del (sys.modules[name])
