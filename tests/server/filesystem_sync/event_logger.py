from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from watchdog.events import FileSystemEvent


@dataclass(frozen=True, eq=True, order=True)
class Event:
    event_type: str = field(compare=True)
    is_directory: bool = field(compare=True)
    src_path: str = field(compare=True)
    dest_path: str = field(compare=True)


_events = set()


def _to_event(e: FileSystemEvent) -> Event:
    event = Event(e.event_type, e.is_directory, e.src_path, e.dest_path)
    return event


def _simplify(e: Event) -> Event:
    src_path = '' if e.src_path is '' else 'src'
    dest_path = '' if e.dest_path is '' else 'dest'
    return Event(e.event_type, e.is_directory, src_path, dest_path)


def log_filesystem_events(events: List[FileSystemEvent]):
    try:
        for e in events:
            event = _simplify(_to_event(e))
            _events.add(event)
        sorted_events = sorted(_events)
        Path('/tmp/events.txt').write_text('\n'.join([str(e) for e in sorted_events]))
    except Exception as ex:
        pass
