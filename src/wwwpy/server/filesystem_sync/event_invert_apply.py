import dataclasses
import shutil
from pathlib import Path
from typing import List

from wwwpy.server.filesystem_sync import Event


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    path_tracker = {}
    """This is a map that keep track of the path changes, starting backwards from the A_n state.
    It's a map <path of the instant i>:<final path in A_n>"""

    def augment(event: Event) -> Event:
        if event.event_type == 'modified':
            path = path_tracker.get(event.src_path, event.src_path)
            content = _get_content(Path(fs / path))
            aug = dataclasses.replace(event, content=content)
            return aug
        return event

    relative_events = []
    for e in reversed(events):
        if e.event_type == 'moved':
            # update the path tracker with the new path keep in mind we are going backwards
            # we are going from A_n to A_(n-1) to A_(n-2) and so on
            # when processing a 'moved' event e_n and creating E_n the event.dest_path is what
            # we want to keep throughout the path_tracker
            instant_path = path_tracker.get(e.dest_path, None)
            if instant_path is None:
                # this is the first rename backwards
                path_tracker[e.src_path] = e.dest_path
            else:
                path_tracker[e.src_path] = e.dest_path

        aug = augment(e)
        rel = aug.relative_to(fs)
        relative_events.insert(0, rel)

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
