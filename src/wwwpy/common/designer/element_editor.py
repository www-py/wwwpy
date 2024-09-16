from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import element_library as el
from . import element_path as ep
from abc import ABC, abstractmethod

from . import code_info


class AttributeEditor(ABC):
    definition: el.AttributeDef
    exists: bool
    value: str | None


class EventEditor:
    definition: el.EventDef
    handled: bool = False

    def __init__(self, event_def: el.EventDef, handled: bool):
        self.handled = handled
        self.definition = event_def

    def do_action(self):
        pass


class ElementEditor:
    attributes: list[AttributeEditor]
    events: list[EventEditor]

    def __init__(self, element_path: ep.ElementPath, element_def: el.ElementDef):
        self.events = []
        python_source = Path(element_path.concrete_path).read_text()
        ci = code_info.class_info(python_source, element_path.class_name)
        data_name = element_path.data_name
        for event in element_def.events:
            method_name = f'{data_name}__{event.name}'
            method = ci.methods_by_name.get(method_name, None)
            self.events.append(EventEditor(event, True if method else False))
