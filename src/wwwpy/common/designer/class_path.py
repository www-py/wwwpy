from __future__ import annotations

from dataclasses import dataclass


@dataclass()
class ClassPath:
    class_module: str
    """The module name of the Component."""
    class_name: str
    """The class name of the Component."""
