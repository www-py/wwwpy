from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, List

from wwwpy.common.rpc import serialization


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
    gen_html: Optional[Callable[[str], str]] = None
    """A function that generates the HTML for the element. It takes the data-name of the element as argument."""

    attributes: list[AttributeDef] = field(default_factory=list)
    events: list[EventDef] = field(default_factory=list)

    def new_html(self, data_name: str) -> str:
        return self.gen_html(data_name) if self.gen_html else \
            f'<{self.tag_name} data-name="{data_name}"></{self.tag_name}>'


class ElementLibrary:
    def __init__(self):
        self.elements: List[ElementDef] = []


_element_library: ElementLibrary = None


def element_library() -> ElementLibrary:
    global _element_library
    if _element_library is None:
        _element_library = ElementLibrary()
        shoelace_json = (Path(__file__).parent / 'shoelace.json').read_text()
        elements = serialization.from_json(shoelace_json, List[ElementDef])
        _element_library.elements.extend(elements)
    return _element_library
