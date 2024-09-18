from __future__ import annotations

from dataclasses import dataclass, field
from .html_parser_mod import HTMLParser
from typing import Tuple, Dict, List


@dataclass
class CstAttribute:
    name: str
    value: str | None
    name_span: Tuple[int, int]
    value_span: Tuple[int, int] | None
    """The span of the attribute value in the HTML string including the quotes char."""


def cst_attribute_dict(*attributes: CstAttribute) -> Dict[str, CstAttribute]:
    return {attr.name: attr for attr in attributes}


@dataclass
class CstNode:
    tag_name: str
    span: Tuple[int, int]
    attr_span: Tuple[int, int]
    """The span of the attributes part. If there is no span the tuple will contain the same value."""
    
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

    def cst_attribute(self, name: str) -> CstAttribute | None:
        for attr in self.attributes_list:
            if attr.name == name:
                return attr
        return None


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

    def handle_starttag_extended(self, tag, attrs, attrs_extended, autoclosing):
        start_pos = self.current_pos

        def _cst_attr(name, v) -> CstAttribute:
            return CstAttribute(name, v['value'], v['name_span'], v['value_span'])

        text = self.get_starttag_text()
        end_displ = 2 if autoclosing else 1
        attr_span = (start_pos + len(tag) + 1, self.current_pos + len(text) - end_displ)
        node = CstNode(
            tag_name=tag,
            span=(start_pos, None),
            attr_span=attr_span,
            attributes_list=[_cst_attr(name, v) for name, v in attrs_extended.items()]
        )

        if self.stack:
            self.stack[-1].children.append(node)

        if tag not in self.void_tags:
            self.stack.append(node)
        else:
            node.span = (start_pos, self.current_pos + len(text))
            if not self.stack:
                self.nodes.append(node)

        self.current_pos += len(text)

    def handle_endtag(self, tag):
        if tag in self.void_tags:  # a void tag with end tag
            return
        if not self.stack:
            return

        node = self.stack.pop()
        node.span = (node.span[0], self.current_pos + len(tag) + 3)  # +3 for </ and >
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
        start, end = node.span
        node.html = html[start:end]
        _compile_html(node.html, node.children)
