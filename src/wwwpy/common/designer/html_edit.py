"""This module contains the HTML string manipulator functions."""
from __future__ import annotations

from enum import Enum

from wwwpy.common.designer.html_locator import NodePath, locate


class Position(str, Enum):
    inside = 'inside'
    beforebegin = 'beforebegin'
    afterend = 'afterend'


def html_add(html: str, add: str, node_path: NodePath, position: Position) -> str:
    """This function adds an HTML piece to the specified position in the HTML string."""

    start, end = locate(html, node_path)

    index = start if position == Position.beforebegin else end

    return html[:index] + add + html[index:]
