import dataclasses
import shutil
from pathlib import Path
from typing import List

from wwwpy.server.filesystem_sync import Event


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    """events paths should already be absolute contained in fs.
    The returned events will be relative to fs."""

    def validate(e: Event):
        if e.src_path == '' or e.src_path == '/':
            raise ValueError(f'Invalid src_path: {e.src_path}')
        src = Path(e.src_path).relative_to(fs)
        res = dataclasses.replace(e, src_path=str(src))

        if e.dest_path == '':
            return res
        if e.dest_path and (e.dest_path == '' or e.dest_path == '/'):
            raise ValueError(f'Invalid dest_path: {e.dest_path}')
        dst = Path(e.dest_path).relative_to(fs)
        res2 = dataclasses.replace(res, dest_path=str(dst))
        return res2

    relative_events = [validate(e) for e in events]

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
