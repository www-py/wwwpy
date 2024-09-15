from __future__ import annotations

from dataclasses import dataclass

from . import element_library as el
from . import element_path as ep
from abc import ABC, abstractmethod


class AttributeEditor(ABC):
    definition: el.AttributeDef
    exists: bool
    value: str | None


class EventEditor(ABC):
    definition: el.EventDef
    handled: bool


class ElementEditor:

    def __init__(self, element_path: ep.ElementPath, element_def: el.ElementDef):
        super().__init__()

    attributes: list[AttributeEditor]
    events: list[EventEditor]
