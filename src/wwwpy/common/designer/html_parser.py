from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Tuple, Dict, List


@dataclass()
class CstNode:
    tag_name: str
    position: Tuple[int, int]
    children: List['CstNode'] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)


class _PositionalHTMLParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self, data):
        super().__init__()
        self.data = data
        self._tree: List[CstNode] = []
        self.stack: List[CstNode] = []

    def handle_starttag(self, tag, attrs):
        position = (self.getpos()[1], self.getpos()[1] + len(tag) + 2)  # Rough estimation of the tag length
        attributes = {k: v for k, v in attrs}
        node = CstNode(tag_name=tag, position=position, attributes=attributes)
        if self.stack:
            self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)
        else:
            self._tree.append(node)

    def handle_endtag(self, tag):
        if self.stack:
            node = self.stack.pop()
            node.position = (node.position[0], self.getpos()[1] + len(tag) + 3)
            if not self.stack:
                self._tree.append(node)

    def handle_startendtag(self, tag, attrs):
        position = (self.getpos()[1], self.getpos()[1] + len(tag) + 3)  # Rough estimation of the tag length
        attributes = {k: v for k, v in attrs}
        node = CstNode(tag_name=tag, position=position, attributes=attributes)
        if self.stack:
            self.stack[-1].children.append(node)
        else:
            self._tree.append(node)

    def handle_data(self, data):
        pass  # Data is ignored for now

    def parse(self):
        self.feed(self.data)
        return self._tree


def html_to_tree(html: str) -> List[CstNode]:
    parser = _PositionalHTMLParser(html)
    return parser.parse()
