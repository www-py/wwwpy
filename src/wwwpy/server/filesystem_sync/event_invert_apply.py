import shutil
from pathlib import Path
from typing import List

from wwwpy.server.filesystem_sync import Event


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    return events


def events_apply(fs: Path, events: List[Event]):
    for event in events:
        _event_apply(fs, event)


def _event_apply(fs: Path, event: Event):
    if event.event_type == 'created':
        if event.is_directory:
            (fs / event.src_path).mkdir()
        else:
            (fs / event.src_path).touch()
    elif event.event_type == 'deleted':
        if event.is_directory:
            shutil.rmtree(fs / event.src_path)
        else:
            (fs / event.src_path).unlink()
