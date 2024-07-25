from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass()
class Node:
    tag_name: str
    child_index: int
    """This is the index in the list of children of the parent node.
    It is -1 if the node has no parent.
    """
    attributes: Dict[str, str]


NodePath = List[Node]
"""This is the path from the root to a node in the DOM tree."""


def node_path_serialize(path: NodePath) -> str:
    return json.dumps([node.__dict__ for node in path])

def node_path_deserialize(serialized: str) -> NodePath:
    node_dicts = json.loads(serialized)
    return [Node(**node_dict) for node_dict in node_dicts]

def locate(html: str, path: NodePath) -> Tuple[int, int] | None:
    """This function locates the position of a node in the HTML string.
    It returns the start and end positions of the node in the HTML string or None if the node is not found."""
    pass
