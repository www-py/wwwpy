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
        self.current_pos = 0

    def handle_starttag(self, tag, attrs):
        self._tree.append((tag, '<', attrs, self.getpos()))

    def handle_endtag(self, tag):
        self._tree.append((tag, '>', self.getpos()))

    def handle_startendtag(self, tag, attrs):
        self._tree.append((tag, '/', attrs, self.getpos()))

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
    parser = _PositionalHTMLParser(html_data)
    position_map = parser.parse()
    return []
