from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

from wwwpy.common.designer.html_locator import NodePath
from wwwpy.common.modlib import _find_module_root


# rename to ElementCodePath
@dataclass()
class ResolvedLocation:
    class_name: str
    """The class name of the Component."""
    class_module: str
    """The module name of the Component."""
    relative_path: str
    """The file path of the .py containing the class, starting from the root of the module path"""
    concrete_path: str
    """The file path of the .py containing the class, as it was discovered"""
    path: NodePath
    """The path from the Component (excluded) to the target."""

@dataclass()
class ElementPath:
    """Contains the path to an element relative to a Component."""

    component: Any | None
    """The Component that contains the element. None if there is no parent Component"""
    path: NodePath
    """The path from the Component (excluded) to the element."""

    def resolve(self) -> ResolvedLocation | None:
        clazz = self.component.__class__
        full_path = inspect.getfile(clazz)
        cn = clazz.__name__
        cm = clazz.__module__
        fqn = f"{cm}.{cn}"
        source_file = _find_module_root(fqn, full_path)
        return ResolvedLocation(class_name=cn,
                                class_module=cm,
                                relative_path=source_file, concrete_path=full_path,
                                path=self.path)
