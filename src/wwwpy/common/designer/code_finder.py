"""At the time of writing this module is used only browser-side,
even though it is in common because of no platform specific dependencies."""
from __future__ import annotations

import inspect
from pathlib import Path


def find_source_file(clazz) -> Path | None:
    """
    Find the source file for a given class.
    E.g., given a [wwwpy.remote.component.Component] it will return the path to the file where the class is defined.
    """
    try:
        file_path = inspect.getfile(clazz)
        path = Path(file_path)
        return path if path.exists() else None
    except TypeError:
        return None
