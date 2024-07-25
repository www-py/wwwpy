from __future__ import annotations

from typing import List

from js import HTMLElement, Array

from wwwpy.common.designer.html_locator import Node, NodePath


def target_path(target: HTMLElement) -> NodePath:
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
