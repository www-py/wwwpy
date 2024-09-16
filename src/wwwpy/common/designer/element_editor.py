from __future__ import annotations

from dataclasses import dataclass

from . import element_library as el
from . import element_path as ep
from abc import ABC, abstractmethod


class AttributeEditor(ABC):
    definition: el.AttributeDef
    exists: bool
    value: str | None


class EventEditor:
    definition: el.EventDef
    handled: bool = False

    def __init__(self, event_def: el.EventDef):
        self.handled = False
        self.definition = event_def

    def do_action(self):
        pass


class ElementEditor:
    attributes: list[AttributeEditor]
    events: list[EventEditor]

    def __init__(self, element_path: ep.ElementPath, element_def: el.ElementDef):
        self.events = []
        for event in element_def.events:
            self.events.append(EventEditor(event))
