from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Tuple, Dict, List


@dataclass()
class CstNode:
    """Concrete syntax tree node"""
    tag_name: str
    position: Tuple[int, int]
    children: List['CstNode'] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)


class _PositionalHTMLParser(HTMLParser):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self._tree: List[CstNode] = []
        self._stack: List[CstNode] = []
        self.current_pos = 0

    def handle_starttag(self, tag, attrs):
        start_pos = self.getpos()
        node = CstNode(tag_name=tag, position=(start_pos[1], -1), attributes=dict(attrs))
        if self._stack:
            self._stack[-1].children.append(node)
        else:
            self._tree.append(node)
        self._stack.append(node)

    def handle_endtag(self, tag):
        end_pos = self.getpos()
        if self._stack:
            node = self._stack.pop()
            node.position = (node.position[0], end_pos[1])

    def handle_startendtag(self, tag, attrs):
        pos = self.getpos()
        node = CstNode(tag_name=tag, position=(pos[1], pos[1]), attributes=dict(attrs))
        if self._stack:
            self._stack[-1].children.append(node)
        else:
            self._tree.append(node)

    def handle_data(self, data):
        self.current_pos += len(data)

    def parse(self):
        self.feed(self.data)
        return self._tree

def main(html_data):
    parser = _PositionalHTMLParser(html_data)
    position_map = parser.parse()

    for pos in position_map:
        print(pos)


def html_to_tree(html: str) -> List[CstNode]:
    parser = _PositionalHTMLParser(html)
    return parser.parse()