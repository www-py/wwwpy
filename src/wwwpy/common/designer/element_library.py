from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Help:
    url: str
    description: str


@dataclass
class NameHelp:
    name: str
    help: Help


@dataclass
class AttributeDef(NameHelp):
    values: list[str] = field(default_factory=list)
    closed_values: bool = False
    mandatory: bool = False
    default_value: str | None = None


@dataclass
class EventDef(NameHelp): ...


_empty_help = Help("", "")


@dataclass
class ElementDef:
    tag_name: str
    python_type: str
    help: Help = field(default=_empty_help)
    gen_html: Callable[[str], str] | None = None
    """A function that generates the HTML for the element. It takes the data-name of the element as argument."""

    attributes: list[AttributeDef] = field(default_factory=list)
    events: list[EventDef] = field(default_factory=list)

    def new_html(self, data_name: str) -> str:
        return self.gen_html(data_name) if self.gen_html else \
            f'<{self.tag_name} data-name="{data_name}"></{self.tag_name}>'


class ElementLibrary:
    def __init__(self):
        self.elements: dict[str, ElementDef] = {}

    def add_element(self, element_def: ElementDef):
        self.elements[element_def.tag_name] = element_def

    def get_element(self, tag_name: str) -> ElementDef | None:
        return self.elements.get(tag_name, None)
