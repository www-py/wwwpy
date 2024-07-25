from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Tuple, Dict, List

@dataclass
class CstNode:
    tag_name: str
    position: Tuple[int, int]
    children: List['CstNode'] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)

class _PositionalHTMLParser(HTMLParser):
    def __init__(self, html: str):
        super().__init__()
        self.html = html
        self.nodes = []
        self.stack = []
        self.current_pos = 0
        self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

    def handle_starttag(self, tag, attrs):
        start_pos = self.current_pos
        attributes = dict(attrs)
        node = CstNode(tag_name=tag, position=(start_pos, None), attributes=attributes)

        if self.stack:
            self.stack[-1].children.append(node)

        if tag not in self.void_tags:
            self.stack.append(node)
        else:
            node.position = (start_pos, self.current_pos + len(self.get_starttag_text()))
            if not self.stack:
                self.nodes.append(node)

        self.current_pos += len(self.get_starttag_text())

    def handle_endtag(self, tag):
        if not self.stack:
            return

        node = self.stack.pop()
        node.position = (node.position[0], self.current_pos + len(tag) + 3)  # +3 for </ and >
        if not self.stack:
            self.nodes.append(node)

        self.current_pos += len(tag) + 3

    def handle_data(self, data):
        self.current_pos += len(data)

    def parse(self):
        self.feed(self.html)
        return self.nodes

def html_to_tree(html: str) -> List[CstNode]:
    parser = _PositionalHTMLParser(html)
    return parser.parse()
