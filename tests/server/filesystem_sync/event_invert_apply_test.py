"""
E = event_invert(A_n, e)
A_n = event_apply(A_0, E)

The tests of this module are created with the following steps:
- GIVEN
    - the initial state of the filesystem A_0
    - the events E
    - the expected state of the filesystem after the event is applied A_n
- WHEN invoke target
- THEN assert the result
"""
import dataclasses
from pathlib import Path
from typing import List

import pytest

from tests.server.filesystem_sync.sync_fixture import _deserialize_events
from wwwpy.server.filesystem_sync import Event


class FilesystemFixture:
    def __init__(self, tmp_path: Path, ):
        self.tmp_path = tmp_path

        def mk(dir):
            p = tmp_path / dir
            p.mkdir(parents=True, exist_ok=True)
            return p

        self.initial_fs = mk('initial')
        self.expected_fs = mk('expected')


@pytest.fixture
def target(tmp_path):
    print(f'\ntmp_path file://{tmp_path}')
    fixture = FilesystemFixture(tmp_path)
    yield fixture


def test_new_file(target):
    # GIVEN
    new_file = target.expected_fs / 'new_file.txt'
    new_file.touch()

    # WHEN
    events = """{"event_type": "created", "is_directory": true, "src_path": "new_file.txt"}"""

    invert_apply(target.expected_fs, events, target.initial_fs)

    # THEN
    assert (target.initial_fs / 'new_file.txt').exists()


def test_delete_file(target):
    # GIVEN
    file = target.initial_fs / 'file.txt'
    file.touch()

    # WHEN
    events = """{"event_type": "deleted", "is_directory": false, "src_path": "file.txt"}"""

    invert_apply(target.expected_fs, events, target.initial_fs)

    # THEN
    assert not (target.initial_fs / 'file.txt').exists()


def invert_apply(expected_fs: Path, events_str: str, initial_fs: Path):
    expected_fs.mkdir(parents=True, exist_ok=True)
    initial_fs.mkdir(parents=True, exist_ok=True)
    events = _deserialize_events(events_str)

    def relocate(e: Event) -> Event:
        src_path = '' if e.src_path == '' else str(initial_fs / e.src_path)
        dest_path = '' if e.dest_path == '' else str(initial_fs / e.dest_path)
        return dataclasses.replace(e, src_path=src_path, dest_path=dest_path)

    events_fix = [relocate(e) for e in events]

    inverted = events_invert(expected_fs, events_fix)
    events_apply(expected_fs, inverted)


# production code
def events_invert(fs: Path, events: List[Event]) -> List[Event]:
    return events


def events_apply(fs: Path, events: List[Event]):
    for event in events:
        event_apply(fs, event)


def event_apply(fs: Path, event: Event):
    if event.event_type == 'created':
        (fs / event.src_path).touch()
    elif event.event_type == 'deleted':
        (fs / event.src_path).unlink()
