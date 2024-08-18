import dataclasses
import shutil
from pathlib import Path
from typing import List

from wwwpy.server.filesystem_sync import Event


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    relative_events = [e.relative_to(fs) for e in events]
    return relative_events


def events_apply(fs: Path, events: List[Event]):
    for event in events:
        _event_apply(fs, event)


def _event_apply(fs: Path, event: Event):
    path = fs / event.src_path
    if event.event_type == 'created':
        if event.is_directory:
            path.mkdir()
        else:
            path.touch()
    elif event.event_type == 'deleted':
        if event.is_directory:
            shutil.rmtree(path)
        else:
            path.unlink()
    elif event.event_type == 'moved':
        shutil.move(path, fs / event.dest_path)
