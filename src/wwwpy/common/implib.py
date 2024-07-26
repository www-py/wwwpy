from __future__ import annotations

from pathlib import Path


def _find_module_path(module_name) -> Path | None:
    import importlib.util

    spec = importlib.util.find_spec(module_name)
    return Path(spec.origin) if spec else None

