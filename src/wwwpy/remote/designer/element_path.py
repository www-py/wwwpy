from __future__ import annotations

from js import Array, Element, document
from wwwpy.common.designer.element_path import ElementPath, Origin
from wwwpy.common.designer.html_locator import Node
from wwwpy.remote.component import get_component


def element_path(element: Element) -> ElementPath | None:
    """Returns an instance of  """

    path = []
    while element:
        component = get_component(element)
        if component:
            clazz = component.__class__
            return ElementPath(clazz.__module__, clazz.__name__, path, Origin.live)
        if element == document.body:
            return None

        parent = element.parentNode
        child_index = Array.prototype.indexOf.call(parent.children, element) if parent else -1
        attributes = {attr.name: attr.value for attr in element.attributes}
        path.insert(0, Node(element.tagName.lower(), child_index, attributes))
        element = parent

    return None
