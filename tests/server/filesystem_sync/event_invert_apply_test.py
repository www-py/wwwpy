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
import shutil
from pathlib import Path
from typing import List

import pytest

from tests.server.filesystem_sync.fs_compare import FsCompare
from tests.server.filesystem_sync.sync_fixture import _deserialize_events
from wwwpy.server.filesystem_sync import Event
from wwwpy.server.filesystem_sync.event_invert_apply import events_invert, events_apply


class FilesystemFixture:
    def __init__(self, tmp_path: Path, ):
        self.tmp_path = tmp_path

        def mk(dir):
            p = tmp_path / dir
            p.mkdir(parents=True, exist_ok=True)
            return p

        self.initial_fs = mk('initial')
        self.expected_fs = mk('expected')
        self.fs_compare = FsCompare(self.initial_fs, self.expected_fs, 'initial', 'expected')

    def assert_filesystem_are_equal(self):
        __tracebackhide__ = True
        assert self.fs_compare.synchronized(), self.fs_compare.sync_error()

    def invoke(self, events_str: str):
        invert_apply(self.expected_fs, events_str, self.initial_fs)


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
    target.invoke("""{"event_type": "created", "is_directory": false, "src_path": "new_file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_file.txt').exists()


def test_delete_file(target):
    # GIVEN
    file = target.initial_fs / 'file.txt'
    file.touch()

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": false, "src_path": "file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'file.txt').exists()


def test_new_directory(target):
    # GIVEN
    new_dir = target.expected_fs / 'new_dir'
    new_dir.mkdir()

    # WHEN
    target.invoke("""{"event_type": "created", "is_directory": true, "src_path": "new_dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_dir').exists()
    assert (target.initial_fs / 'new_dir').is_dir()


def test_delete_directory(target):
    # GIVEN
    dir = target.initial_fs / 'dir'
    dir.mkdir()

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": true, "src_path": "dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'dir').exists()


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
