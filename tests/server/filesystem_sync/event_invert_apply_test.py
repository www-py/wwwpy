"""
e_list = [e_1, e_2, e_n ]

E_list = event_invert(A_n, e_list)
A_n = event_apply(A_0, E_list)

The tests of this module are created with the following steps:
- GIVEN
    - the initial state of the filesystem A_0
    - the events E_list
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
        events = _deserialize_events(events_str)

        def relocate(e: Event, into: Path) -> Event:
            src_path = '' if e.src_path == '' else str(into / e.src_path)
            dest_path = '' if e.dest_path == '' else str(into / e.dest_path)
            return dataclasses.replace(e, src_path=src_path, dest_path=dest_path)

        events_fix = [relocate(e, self.expected_fs) for e in events]

        inverted = events_invert(self.expected_fs, events_fix)
        events_apply(self.initial_fs, inverted)

    def source_mutate(self):
        """This transform the initial_fs into the expected_fs.
        In other words it should generate events e_list that when applied to A_0 should result in A_n"""
        return Mutator(self.expected_fs)

    def source_init(self):
        """This should be used to create the initial state of the filesystem.
        In other words this is setting up the A_0 filesystem"""

        def on_exit():
            shutil.rmtree(self.expected_fs, ignore_errors=True)
            shutil.copytree(self.initial_fs, self.expected_fs, dirs_exist_ok=True)

        return Mutator(self.initial_fs, on_exit)


class Mutator:
    def __init__(self, fs: Path, on_exit=None):
        self.fs = fs
        self.on_exit = on_exit

    def touch(self, path: str):
        (self.fs / path).touch()

    def mkdir(self, path: str):
        (self.fs / path).mkdir()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.on_exit:
            self.on_exit()

    def unlink(self, path: str):
        (self.fs / path).unlink()

    def rmdir(self, path):
        (self.fs / path).rmdir()


@pytest.fixture
def target(tmp_path):
    print(f'\ntmp_path file://{tmp_path}')
    fixture = FilesystemFixture(tmp_path)
    yield fixture


def test_new_file(target):
    # GIVEN
    with target.source_mutate() as source:
        source.touch('new_file.txt')

    # WHEN
    target.invoke("""{"event_type": "created", "is_directory": false, "src_path": "new_file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_file.txt').exists()


def test_delete_file(target):
    # GIVEN
    with target.source_init() as source:
        source.touch('file.txt')

    with target.source_mutate() as source:
        source.unlink('file.txt')

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": false, "src_path": "file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'file.txt').exists()


def test_new_directory(target):
    # GIVEN
    with target.source_mutate() as source:
        source.mkdir('new_dir')

    # WHEN
    target.invoke("""{"event_type": "created", "is_directory": true, "src_path": "new_dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_dir').exists()
    assert (target.initial_fs / 'new_dir').is_dir()


def test_delete_directory(target):
    # GIVEN
    with target.source_init() as source:
        source.mkdir('dir')

    with target.source_mutate() as source:
        source.rmdir('dir')

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": true, "src_path": "dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'dir').exists()


def xx_test_move_file(target):
    # GIVEN
    file = target.initial_fs / 'f.txt'
    file.touch()

    # WHEN
    target.invoke("""{"event_type": "moved", "is_directory": false, "src_path": "f.txt", "dest_path": "f2.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'f.txt').exists()
    assert (target.initial_fs / 'f2.txt').exists()
