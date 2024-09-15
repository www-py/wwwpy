from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass()
class Node:
    tag_name: str
    """The tag name in lowercase."""
    child_index: int
    """This is the index in the list of children of the parent node.
    It is -1 if the node has no parent.
    """
    attributes: Dict[str, str]

    def __post_init__(self):
        assert self.tag_name == self.tag_name.lower()


NodePath = List[Node]
"""This is the path from the root to a node in the DOM tree."""


def node_path_serialize(path: NodePath) -> str:
    return json.dumps([node.__dict__ for node in path])


def node_path_deserialize(serialized: str) -> NodePath:
    node_dicts = json.loads(serialized)
    return [Node(**node_dict) for node_dict in node_dicts]


from wwwpy.common.designer.html_parser import html_to_tree, CstNode


def locate(html: str, path: NodePath) -> Tuple[int, int] | None:
    """This function locates the position of the node specified by the path in the HTML string.
    The position is represented by the start and end indices of the node in the HTML string.
    """
    # Parse the HTML to get the tree of CstNode objects
    cst_tree = html_to_tree(html)

    def find_node(nodes: List[CstNode], path: NodePath, depth: int) -> CstNode | None:
        if depth >= len(path):
            return None

        target_node = path[depth]
        if target_node.child_index < 0 or target_node.child_index >= len(nodes):
            return None
        node = nodes[target_node.child_index]
        if depth == len(path) - 1:
            return node
        return find_node(node.children, path, depth + 1)

    target_node = find_node(cst_tree, path, 0)

    if target_node:
        return target_node.position
    return None
