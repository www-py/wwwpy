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
import shutil
from pathlib import Path
from typing import List, AnyStr

import pytest

from tests.server.filesystem_sync.fs_compare import FsCompare
from tests.server.filesystem_sync.sync_fixture import _deserialize_events
from wwwpy.server.filesystem_sync import Event
from wwwpy.server.filesystem_sync.event_invert_apply import events_invert, events_apply


class FilesystemFixture:
    def __init__(self, tmp_path: Path, ):
        self.tmp_path = tmp_path

        def mk(path):
            p = tmp_path / path
            p.mkdir(parents=True, exist_ok=True)
            return p

        self.initial_fs = mk('initial')
        self.expected_fs = mk('expected')
        self.fs_compare = FsCompare(self.initial_fs, self.expected_fs, 'initial', 'expected')
        self.source_mutator = Mutator(self.expected_fs)
        """This transform the initial_fs into the expected_fs.
    In other words it should execute the operations that will create 
    events e_list that when applied to A_0 should result in A_n"""

    def assert_filesystem_are_equal(self):
        __tracebackhide__ = True
        assert self.fs_compare.synchronized(), self.fs_compare.sync_error()

    def invoke(self, events_str: str):
        events = _deserialize_events(events_str)

        # verify that we specified events_str correctly
        assert self.source_mutator.events == events

        events_fix = [e.to_absolute(self.expected_fs) for e in events]

        inverted = events_invert(self.expected_fs, events_fix)
        events_apply(self.initial_fs, inverted)

    @property
    def source_init(self):
        """This should be used to create the initial state of the filesystem.
        In other words this is setting up the A_0 filesystem"""

        def on_init_exit():
            shutil.rmtree(self.expected_fs, ignore_errors=True)
            shutil.copytree(self.initial_fs, self.expected_fs, dirs_exist_ok=True)

        return Mutator(self.initial_fs, on_init_exit)


class Mutator:
    def __init__(self, fs: Path, on_exit=None):
        self.fs = fs
        self.on_exit = on_exit
        self.events: List[Event] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.on_exit:
            self.on_exit()

    def touch(self, path: str):
        self.events.append(Event(event_type='created', is_directory=False, src_path=path))
        (self.fs / path).touch()

    def mkdir(self, path: str):
        self.events.append(Event(event_type='created', is_directory=True, src_path=path))
        (self.fs / path).mkdir()

    def unlink(self, path: str):
        self.events.append(Event(event_type='deleted', is_directory=False, src_path=path))
        (self.fs / path).unlink()

    def rmdir(self, path):
        self.events.append(Event(event_type='deleted', is_directory=True, src_path=path))
        (self.fs / path).rmdir()

    def move(self, old, new):
        fs_old = self.fs / old
        self.events.append(Event(event_type='moved', is_directory=fs_old.is_dir(), src_path=old, dest_path=new))
        shutil.move(fs_old, self.fs / new)

    def write(self, path: str, content: AnyStr):
        self.events.append(Event(event_type='modified', is_directory=False, src_path=path))
        p = self.fs / path
        if isinstance(content, bytes):
            p.write_bytes(content)
        elif isinstance(content, str):
            p.write_text(content)
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")


@pytest.fixture
def target(tmp_path):
    print(f'\ntmp_path file://{tmp_path}')
    fixture = FilesystemFixture(tmp_path)
    yield fixture


def test_new_file(target):
    # GIVEN
    with target.source_mutator as m:
        m.touch('new_file.txt')

    # WHEN
    target.invoke("""{"event_type": "created", "is_directory": false, "src_path": "new_file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_file.txt').exists()


def test_delete_file(target):
    # GIVEN
    with target.source_init as m:
        m.touch('file.txt')

    with target.source_mutator as m:
        m.unlink('file.txt')

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": false, "src_path": "file.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'file.txt').exists()


def test_new_directory(target):
    # GIVEN
    with target.source_mutator as m:
        m.mkdir('new_dir')

    # WHEN
    target.invoke("""{"event_type": "created", "is_directory": true, "src_path": "new_dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert (target.initial_fs / 'new_dir').exists()
    assert (target.initial_fs / 'new_dir').is_dir()


def test_delete_directory(target):
    # GIVEN
    with target.source_init as m:
        m.mkdir('dir')

    with target.source_mutator as m:
        m.rmdir('dir')

    # WHEN
    target.invoke("""{"event_type": "deleted", "is_directory": true, "src_path": "dir"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'dir').exists()


def test_move_file(target):
    # GIVEN
    with target.source_init as m:
        m.touch('f.txt')

    with target.source_mutator as m:
        m.move('f.txt', 'f2.txt')

    # WHEN
    target.invoke("""{"event_type": "moved", "is_directory": false, "src_path": "f.txt", "dest_path": "f2.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'f.txt').exists()
    assert (target.initial_fs / 'f2.txt').exists()


def test_move_directory(target):
    # GIVEN
    with target.source_init as m:
        m.mkdir('dir')

    with target.source_mutator as m:
        m.move('dir', 'dir2')

    # WHEN
    target.invoke("""{"event_type": "moved", "is_directory": true, "src_path": "dir", "dest_path": "dir2"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'dir').exists()
    assert (target.initial_fs / 'dir2').exists()
    assert (target.initial_fs / 'dir2').is_dir()


def test_move_file_to_directory(target):
    # GIVEN
    with target.source_init as m:
        m.touch('f.txt')
        m.mkdir('dir')

    with target.source_mutator as m:
        m.move('f.txt', 'dir/f.txt')

    # WHEN
    target.invoke("""{"event_type": "moved", "is_directory": false, "src_path": "f.txt", "dest_path": "dir/f.txt"}""")

    # THEN
    target.assert_filesystem_are_equal()
    assert not (target.initial_fs / 'f.txt').exists()
    assert (target.initial_fs / 'dir/f.txt').exists()


def test_change_file_text(target):
    # GIVEN
    with target.source_init as m:
        m.touch('f.txt')

    with target.source_mutator as m:
        m.write('f.txt', 'new content')

    # WHEN
    target.invoke("""{"event_type": "modified", "is_directory": false, "src_path": "f.txt"}""")

    # THEN
    assert Path(target.initial_fs / 'f.txt').read_text() == 'new content'
    target.assert_filesystem_are_equal()


def test_change_file_binary(target):
    # GIVEN
    with target.source_init as m:
        m.touch('f.txt')

    with target.source_mutator as m:
        m.write('f.txt', b'\x80\x81\x82')

    # WHEN
    target.invoke("""{"event_type": "modified", "is_directory": false, "src_path": "f.txt"}""")

    # THEN
    assert Path(target.initial_fs / 'f.txt').read_bytes() == b'\x80\x81\x82'
    target.assert_filesystem_are_equal()


def test_create_modify_rename(target):
    # GIVEN
    with target.source_init as m:
        m.touch('f.txt')

    with target.source_mutator as m:
        m.write('f.txt', 'new content')
        m.move('f.txt', 'f2.txt')

    # WHEN
    target.invoke("""
    {"event_type": "modified", "is_directory": false, "src_path": "f.txt"}\n
    {"event_type": "moved", "is_directory": false, "src_path": "f.txt", "dest_path": "f2.txt"}""")

    # THEN
    assert Path(target.initial_fs / 'f2.txt').read_text() == 'new content'
    target.assert_filesystem_are_equal()


def test_create_modify_rename_folder(target):
    # GIVEN
    with target.source_init as m:
        m.mkdir('dir')

    with target.source_mutator as m:
        m.write('dir/f.txt', 'new content')
        m.move('dir', 'dir2')

    # WHEN
    target.invoke("""
    {"event_type": "modified", "is_directory": false, "src_path": "dir/f.txt"}\n
    {"event_type": "moved", "is_directory": true, "src_path": "dir", "dest_path": "dir2"}""")

    # THEN
    assert Path(target.initial_fs / 'dir2/f.txt').read_text() == 'new content'
    target.assert_filesystem_are_equal()
