from __future__ import annotations

import inspect
from pathlib import Path


def find_source_file(clazz) -> Path | None:
    """
    Find the source file for a given class.
    """
    try:
        file_path = inspect.getfile(clazz)
        path = Path(file_path)
        return path if path.exists() else None
    except TypeError:
        return None
