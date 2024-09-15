from __future__ import annotations

from js import Array, Element, document

from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node


def _fqn(obj):
    return f"{obj.__class__.__module__}.{obj.__class__.__name__}"


def element_path(element: Element) -> ElementPath | None:
    """Returns an instance of  """

    path = []
    while element:
        if hasattr(element, "_py"):
            component = element._py
            if hasattr(component, "unwrap"):
                component = component.unwrap()
            return ElementPath(component=component, path=path)
        if element == document.body:
            return None

        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.insert(0, Node(element.tagName, child_index, attributes))
        element = parent

    return None
