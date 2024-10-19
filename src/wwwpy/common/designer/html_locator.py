from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

from wwwpy.common.designer.html_parser import html_to_tree, CstNode, CstTree


@dataclass()
class Node:
    """This is intended to be serializable because it could cross the client/server boundary."""
    tag_name: str
    """The tag name in lowercase."""
    child_index: int
    """This is the index in the list of children of the parent node.
    It is -1 if the node has no parent.
    """
    attributes: Dict[str, Optional[str]]
    """The HTML attributes of the node."""

    def __post_init__(self):
        assert self.tag_name == self.tag_name.lower()

IndexPath = List[int]
NodePath = List[Node]
"""This is the path from the root to a node in the DOM tree."""


def check_node_path(node_path: IndexPath):
    if len(node_path) > 0 and not isinstance(node_path[0], int):
        raise ValueError(f'Invalid node path: {node_path}')

def node_path_serialize(path: NodePath) -> str:
    return json.dumps([node.__dict__ for node in path])


def node_path_deserialize(serialized: str) -> NodePath:
    node_dicts = json.loads(serialized)
    return [Node(**node_dict) for node_dict in node_dicts]


def locate_node(html: str, path: NodePath) -> CstNode | None:
    cst_tree = html_to_tree(html)

    def find_node(nodes: CstTree, path: NodePath, depth: int) -> CstNode | None:
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

    return target_node

def locate_node_indexed(html: str, index_path: IndexPath) -> CstNode | None:
    check_node_path(index_path)
    cst_tree = html_to_tree(html)

    def find_node(nodes: CstTree, path: IndexPath, depth: int) -> CstNode | None:
        if depth >= len(path):
            return None

        child_index = path[depth]
        if child_index < 0 or child_index >= len(nodes):
            return None
        node = nodes[child_index]
        if depth == len(path) - 1:
            return node
        return find_node(node.children, path, depth + 1)

    target_node = find_node(cst_tree, index_path, 0)

    return target_node


def locate_span(html: str, path: NodePath) -> Tuple[int, int] | None:
    """This function locates the position of the node specified by the path in the HTML string.
    The position is represented by the start and end indices of the node in the HTML string.
    """

    node = locate_node(html, path)
    return node.span if node else None

def locate_span_indexed(html: str, index_path: IndexPath) -> Tuple[int, int] | None:
    check_node_path(index_path)
    """This function locates the position of the node specified by the path in the HTML string.
    The position is represented by the start and end indices of the node in the HTML string.
    """

    node = locate_node_indexed(html, index_path)
    return node.span if node else None


def tree_to_path(tree: CstTree, index_path: IndexPath) -> NodePath:
    check_node_path(index_path)
    """This function converts a tree of CstNode objects to a NodePath."""

    def _node(index: int, node: CstNode) -> Node:
        return Node(node.tag_name, index, node.attributes)

    result = []
    children = tree
    for index in index_path:
        node = children[index]
        result.append(_node(index, node))
        children = node.children
    return result


def html_to_node_path(html: str, index_path: IndexPath) -> NodePath:
    check_node_path(index_path)
    tree = html_to_tree(html)
    return tree_to_path(tree, index_path)
