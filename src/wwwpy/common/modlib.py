"""Module library for finding module paths and roots."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def _find_module_path(module_name) -> Path | None:
    """Finds the path of a module without loading it."""
    spec = importlib.util.find_spec(module_name)
    try:
        result = Path(spec.origin) if spec else None
    except:
        import traceback
        print(f'error finding module `{module_name}`: {traceback.format_exc()}')
        result = None
    return result

def _find_package_directory(package_name) -> Path | None:
    """Finds the directory of a package without loading it."""
    path = _find_module_path(package_name)
    if not path:
        return None
    if path.name != '__init__.py':
        raise ValueError(f'package {package_name} is not a package')
    return path.parent

def _find_module_root(fqn, full_path):
    parts = fqn.split('.')
    relative_path = os.path.join(*parts[:-1]) + '.py'
    full_path = os.path.abspath(full_path)
    index = full_path.rfind(relative_path)
    if index == -1:
        return None
    return full_path[index:]
