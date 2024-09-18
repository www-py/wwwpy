"""This module contains the HTML string manipulator functions."""
from __future__ import annotations

from enum import Enum
from html import escape
from wwwpy.common.designer.html_locator import NodePath
from wwwpy.common.designer import html_locator


class Position(str, Enum):
    inside = 'inside'
    beforebegin = 'beforebegin'
    afterend = 'afterend'


def html_add(html: str, add: str, node_path: NodePath, position: Position) -> str:
    """This function adds an HTML piece to the specified position in the HTML string."""

    start, end = html_locator.locate(html, node_path)

    index = start if position == Position.beforebegin else end

    return html[:index] + add + html[index:]


def html_edit(html: str, edit: str, node_path: NodePath) -> str:
    """This function edits the HTML string at the specified path."""
    start, end = html_locator.locate(html, node_path)

    return html[:start] + edit + html[end:]


def html_attribute_set(html: str, node_path: NodePath, attr_name: str, attr_value: str | None) -> str:
    """This function sets an attribute of the specified node in the HTML string.
    When the value is None, the attribute value is remove entirely"""

    node = html_locator.locate_node(html, node_path)
    if node is None:
        print(f'node not found at path={node_path} in html=```{html}```')
        return html

    cst_attr = node.cst_attribute(attr_name)
    vs = cst_attr.value_span
    sep = html[vs[0]]
    left = html[:vs[0]]
    right = html[vs[1]:]

    result = left + sep + escape(attr_value) + sep + right
    return result
