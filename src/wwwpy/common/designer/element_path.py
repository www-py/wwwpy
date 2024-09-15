from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

from wwwpy.common.designer.html_locator import NodePath
from wwwpy.common.modlib import _find_module_root

# could be called ElementLocation
@dataclass()
class ElementPath:
    """Contains the path to an element relative to a Component."""

    component: Any
    """The Component that contains the element"""
    path: NodePath
    """The path from the Component (excluded) to the element."""

    class_name: str = field(init=False)
    """The class name of the Component."""
    class_module: str = field(init=False)
    """The module name of the Component."""
    relative_path: str = field(init=False)
    """The file path of the .py containing the class, starting from the root of the module path"""
    concrete_path: str = field(init=False)
    """The file path of the .py containing the class, as it was discovered"""

    def __post_init__(self):
        clazz = self.component.__class__
        full_path = inspect.getfile(clazz)
        cn = clazz.__name__
        cm = clazz.__module__
        fqn = f"{cm}.{cn}"
        source_file = _find_module_root(fqn, full_path)
        self.class_name = cn
        self.class_module = cm
        self.relative_path = source_file
        self.concrete_path = full_path
