import dataclasses
import shutil
from pathlib import Path
from typing import List

from wwwpy.server.filesystem_sync import Event


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    def augment(event: Event) -> Event:
        if event.event_type == 'modified':
            aug = dataclasses.replace(event, content=_get_content(Path(fs / event.src_path)))
            return aug
        return event

    augmented = [augment(e) for e in events]
    relative_events = [e.relative_to(fs) for e in augmented]
    return relative_events


def events_apply(fs: Path, events: List[Event]):
    for event in events:
        _event_apply(fs, event)


def _event_apply(fs: Path, event: Event):
    path = fs / event.src_path
    t = event.event_type
    is_dir = event.is_directory
    if t == 'created':
        if is_dir:
            path.mkdir()
        else:
            path.touch()
    elif t == 'deleted':
        if is_dir:
            shutil.rmtree(path)
        else:
            path.unlink()
    elif t == 'moved':
        shutil.move(path, fs / event.dest_path)
    elif t == 'modified':
        c = event.content
        if isinstance(c, str):
            path.write_text(c)
        elif isinstance(c, bytes):
            path.write_bytes(c)
        else:
            raise ValueError(f"Unsupported content type: {type(c)}")


def _get_content(path: Path):
    assert path.exists()
    assert path.is_file()
    try:
        return path.read_text()
    except UnicodeDecodeError:
        return path.read_bytes()
