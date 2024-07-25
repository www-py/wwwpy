from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from js import HTMLElement, Array


@dataclass()
class Node:
    tag_name: str
    child_index: int
    """This is the index in the list of children of the parent node.
    It is -1 if the node has no parent.
    """
    attributes: Dict[str, str]


def target_path(target: HTMLElement) -> List[Node]:
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
