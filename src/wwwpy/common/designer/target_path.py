"""could be called code_path ?!"""
from __future__ import annotations

from dataclasses import dataclass

from wwwpy.common.designer.html_locator import NodePath

# it could be split in ClassLocation and the NodePath
@dataclass()
class ResolvedLocation:
    class_name: str
    """The fully qualified class name of the Component."""
    relative_path: str
    """The file path of the .py containing the class, starting from the root of the module path"""
    concrete_path: str
    """The file path of the .py containing the class, as it was discovered"""
    path: NodePath
    """The path from the Component (excluded) to the target."""
