from dataclasses import dataclass, field
from .html_parser_mod import HTMLParser
from typing import Tuple, Dict, List


@dataclass
class CstAttribute:
    name: str
    value: str


def cst_attribute_dict(*attributes: CstAttribute) -> Dict[str, CstAttribute]:
    return {attr.name: attr for attr in attributes}


@dataclass
class CstNode:
    tag_name: str
    position: Tuple[int, int]
    children: List['CstNode'] = field(default_factory=list)
    attributes_list: List[CstAttribute] = field(default_factory=list)
    html: str = field(repr=False, compare=False, default='')

    def __post_init__(self):
        self._attributes_dict = None

    @property
    def attributes(self) -> Dict[str, str]:
        if self._attributes_dict is None:
            self._attributes_dict = {attr.name: attr.value for attr in self.attributes_list}
        return self._attributes_dict


def html_to_tree(html: str) -> List[CstNode]:
    parser = _PositionalHTMLParser(html)
    parse = parser.parse()
    _compile_html(html, parse)
    return parse


class _PositionalHTMLParser(HTMLParser):
    void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

    def __init__(self, html: str):
        super().__init__()
        self.html = html
        self.nodes = []
        self.stack = []
        self.current_pos = 0

    def handle_starttag(self, tag, attrs):
        start_pos = self.current_pos
        node = CstNode(tag_name=tag, position=(start_pos, None),
                       attributes_list=[CstAttribute(name=name, value=value) for name, value in attrs])

        if self.stack:
            self.stack[-1].children.append(node)

        text = self.get_starttag_text()
        if tag not in self.void_tags:
            self.stack.append(node)
        else:
            node.position = (start_pos, self.current_pos + len(text))
            if not self.stack:
                self.nodes.append(node)

        self.current_pos += len(text)

    def handle_endtag(self, tag):
        if tag in self.void_tags:  # a void tag with end tag
            return
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


def _compile_html(html: str, tree: List[CstNode]):
    for node in tree:
        start, end = node.position
        node.html = html[start:end]
        _compile_html(node.html, node.children)
