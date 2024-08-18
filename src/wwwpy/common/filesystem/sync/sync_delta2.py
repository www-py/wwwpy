from pathlib import Path
from typing import List, Any

from wwwpy.common.rpc import serialization
from wwwpy.common.filesystem.sync import Event
from wwwpy.common.filesystem.sync import event_invert_apply


def sync_source(source: Path, events: List[Event]) -> List[Any]:
    events_inverted = event_invert_apply.events_invert(source, events)
    ser = serialization.serialize(events_inverted, List[Event])
    return ser


def sync_target(target_root: Path, changes: List[Any]) -> None:
    events = serialization.deserialize(changes, List[Event])
    event_invert_apply.events_apply(target_root, events)


def sync_init(source: Path) -> List[Any]:
    events = event_invert_apply.events_init(source)
    ser = serialization.serialize(events, List[Event])
    return ser


