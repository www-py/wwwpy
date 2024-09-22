from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, List


@dataclass(frozen=True)
class Help:
    description: str
    url: str


_empty_help = Help("", "")


@dataclass
class NameHelp:
    name: str
    help: Help = field(default=_empty_help)


@dataclass
class EventDef(NameHelp):
    """Definition of an event of an HTML element."""
    pass


@dataclass
class AttributeDef(NameHelp):
    """Definition of an attribute of an HTML element."""
    values: list[str] = field(default_factory=list)
    closed_values: bool = False
    mandatory: bool = False
    default_value: Optional[str] = None


@dataclass
class ElementDef:
    tag_name: str
    python_type: str
    help: Help = field(default=_empty_help)
    gen_html: Optional[Callable[[ElementDef, str], str]] = None
    """A function that generates the HTML for the element. It takes the data-name of the element as argument."""

    attributes: list[AttributeDef] = field(default_factory=list)
    events: list[EventDef] = field(default_factory=list)

    def new_html(self, data_name: str) -> str:
        gen_html = self.gen_html or ElementDef.default_gen_html
        return gen_html(self, data_name)

    @classmethod
    def default_gen_html(cls, element_def: ElementDef, data_name: str) -> str:
        return f'\n<{element_def.tag_name} data-name="{data_name}"></{element_def.tag_name}>'


class ElementLibrary:
    def __init__(self):
        self.elements: List[ElementDef] = []

    def by_tag_name(self, tag_name: str) -> Optional[ElementDef]:
        for element in self.elements:
            if element.tag_name == tag_name:
                return element
        return None


_element_library: ElementLibrary = None


def element_library() -> ElementLibrary:
    global _element_library
    if _element_library is None:
        _element_library = ElementLibrary()
        from wwwpy.common.designer.shoelace import _shoelace_elements_def
        _element_library.elements.extend(_shoelace_elements_def())
    return _element_library
