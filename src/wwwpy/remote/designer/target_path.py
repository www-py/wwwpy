from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from time import sleep
from typing import List

from js import HTMLElement, Array, Element, document

from wwwpy.common.designer.html_locator import Node, NodePath
from wwwpy.common.modlib import _find_module_path, _find_module_root
from wwwpy.remote.component import Component
import inspect


@dataclass()
class ResolvedLocation:
    class_name: str
    """The fully qualified class name of the Component."""
    source_file: str
    """The file path of the .py containing the class, starting from the root of the module path"""
    path: NodePath
    """The path from the Component (excluded) to the target."""


@dataclass()
class TargetLocation:
    """This class represents the location of a target relative to a Component."""
    component: Component | None
    """The Component that contains the target."""
    path: NodePath
    """The path from the Component (excluded) to the target."""

    def resolve(self) -> ResolvedLocation | None:
        full_path = inspect.getfile(self.component.__class__)
        fqn = _fqn(self.component)
        source_file = _find_module_root(fqn, full_path)
        return ResolvedLocation(class_name=_fqn(self.component), source_file=source_file, path=self.path)


def _get_source_file_path(instance):
    cls = instance.__class__
    module = cls.__module__
    source_file_path = inspect.getfile(sys.modules[module])
    return source_file_path


def _fqn(obj):
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def target_location(target: Element) -> TargetLocation:
    """
    Compute the [TargetLocation].
    """

    path = []
    element: Element = target
    while element:
        if hasattr(element, "_py"):
            component = element._py
            return TargetLocation(component=component, path=path)
        if element == document.body:
            return TargetLocation(component=None, path=path)

        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.insert(0, Node(element.tagName, child_index, attributes))
        element = parent

    return TargetLocation(component=None, path=path)


def path_to_target(target: HTMLElement) -> NodePath:
    """
    Get the path from the root to the target.
    """

    path = []
    element = target
    while element:
        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.append(Node(element.tagName, child_index, attributes))
        element = parent
    path.reverse()
    return path
