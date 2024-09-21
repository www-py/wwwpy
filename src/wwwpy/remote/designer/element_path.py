from __future__ import annotations

import js
from js import Array, Element, document

from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node, NodePath


def _fqn(obj):
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def element_path(element: Element) -> ElementPath | None:
    """Returns an instance of  """

    path = []
    while element:
        if hasattr(element, "_py"):
            # todo this should be moved to component.py in a function like component_from_element
            # or get_underlying_component
            component = element._py
            if hasattr(component, "unwrap"):
                component = component.unwrap()
            clazz = component.__class__
            return ElementPath(clazz.__module__, clazz.__name__, path)
        if element == document.body:
            return None

        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.insert(0, Node(element.tagName.lower(), child_index, attributes))
        element = parent

    return None


def element_to_node_path(element: HTMLElement) -> NodePath:
    """
    Get the path from the root to the target.
    """

    path = []
    while element:
        if element == document.body:
            return path
        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.insert(0, Node(element.tagName.lower(), child_index, attributes))
        element = parent

    return path
