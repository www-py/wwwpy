import shutil

import pytest

from tests.server.filesystem_sync.sync_fixture import SyncFixture
from wwwpy.server.filesystem_sync import sync_delta, sync_zip

invalid_utf8 = b'\x80\x81\x82'


@pytest.fixture(params=[sync_delta, sync_zip])
def target(tmp_path, request):
    print(f'\ntmp_path file://{tmp_path}')
    fixture = SyncFixture(tmp_path, sync=request.param)
    yield fixture
    fixture.debounced_watcher.stop()
    fixture.debounced_watcher.join()

# todo this code does not rely on watchdog events generated during testing
# todo, remove the old code and minimize the dependencies

def disable_test_a_read_on_source__should_not_generate_events(target):
    """This is needed because if during the collection of source changes,
    we will fire new events and we will end up in an infinite loop"""
    # GIVEN
    (target.left / 'foo.txt').write_text('content1')
    target.start()

    # WHEN
    (target.left / 'foo.txt').read_text()
    target.wait_at_rest()

    # THEN
    assert target.all_events == [], target.sync_error()


def test_new_file(target):
    # GIVEN
    # target.start()
    (target.source / 'new_file.txt').write_text('new file')
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """

    # WHEN
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert (target.target / 'new_file.txt').exists(), target.sync_error()
    assert (target.target / 'new_file.txt').read_text() == 'new file', target.sync_error()


def test_new_file__optimize(target):
    # GIVEN
    # target.start()
    (target.source / 'new_file.txt').write_text('new file')
    (target.source / 'new_file.txt').write_text('new file2')
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """
    # WHEN
    # changes = target.do_sync()
    changes = target.apply_events(events)

    # THEN
    assert (target.target / 'new_file.txt').exists(), target.sync_error()
    assert (target.target / 'new_file.txt').read_text() == 'new file2', target.sync_error()
    # todo optimize assert len(changes) == 1, target.sync_error()


def test_new_file_and_delete(target):
    # GIVEN
    # target.start()
    (target.source / 'new_file.txt').write_text('new file')
    (target.source / 'new_file.txt').write_text('new file2')
    (target.source / 'new_file.txt').unlink()
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "deleted", "is_directory": false, "src_path": "source/new_file.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  """
    # WHEN
    # changes = target.get_changes()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()


def test_new_file_in_subfolder(target):
    # GIVEN
    # target.start()
    sub1 = target.source / 'sub1'
    sub1.mkdir()
    (sub1 / 'foo.txt').write_text('sub-file')
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "created", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "created", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
    """
    # WHEN
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert (target.target / 'sub1/foo.txt').exists(), target.sync_error()
    assert (target.target / 'sub1/foo.txt').read_text() == 'sub-file', target.sync_error()


def test_delete_file(target):
    # GIVEN
    source_foo = target.source / 'foo.txt'
    source_foo.write_text('content1')
    target_foo = target.target / 'foo.txt'
    target_foo.write_text('content1')
    # target.start()

    source_foo.unlink()
    # target.wait_at_rest()
    events = """
  {"event_type": "deleted", "is_directory": false, "src_path": "source/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """
    # WHEN
    # changes = target.do_sync()
    changes = target.apply_events(events)

    # THEN
    assert not target_foo.exists(), target.sync_error()
    # todo optimize assert len(changes) == 1, target.sync_error()


def test_created(target):
    # GIVEN
    # target.start()
    (target.source / 'foo.txt').touch()
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": false, "src_path": "source/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """
    # WHEN
    # changes = target.do_sync()
    changes = target.apply_events(events)

    # THEN
    assert (target.target / 'foo.txt').exists(), target.sync_error()
    assert (target.target / 'foo.txt').stat().st_size == 0, target.sync_error()
    assert len(changes) == 1


def test_init(target):
    # GIVEN
    (target.source / 'foo.txt').write_text('c1')
    (target.source / 'foo.bin').write_bytes(invalid_utf8)

    # WHEN
    target.do_init()

    # THEN
    assert (target.target / 'foo.txt').read_text() == 'c1', target.sync_error()
    assert (target.target / 'foo.bin').read_bytes() == invalid_utf8, target.sync_error()
    assert target.synchronized(), target.sync_error()


def test_synchronized_no_files(target):
    # GIVEN

    # WHEN
    target.do_init()

    # THEN
    assert target.synchronized()
    assert target.sync_error() is None


def test_synchronized_some_files(target):
    # GIVEN
    (target.source / 'foo.txt').write_text('c1')

    assert target.synchronized() is False
    assert target.sync_error() is not None


def test_delete_folder(target):
    # GIVEN
    (target.source / 'sub1').mkdir()
    (target.source / 'sub1/foo.txt').write_text('content1')
    target.copy_source_to_target()
    # target.start()

    shutil.rmtree(target.source / 'sub1')
    # target.wait_at_rest()
    events = """
  {"event_type": "deleted", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "deleted", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """
    # WHEN
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()


def test_delete_folder__and_recreate_it(target):
    def build():
        (target.source / 'sub1').mkdir()
        (target.source / 'sub1/foo.txt').write_text('content1')

    # GIVEN
    build()
    target.copy_source_to_target()
    # target.start()

    # WHEN
    shutil.rmtree(target.source / 'sub1')
    build()
    # target.wait_at_rest()
    events = """
  {"event_type": "deleted", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "deleted", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "created", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "created", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub1", "dest_path": ""}
"""

    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()


def test_invalid_text(target):
    # GIVEN
    # target.start()

    (target.source / 'foo.bin').write_bytes(invalid_utf8)
    # target.wait_at_rest()
    events = """
  {"event_type": "created", "is_directory": false, "src_path": "source/foo.bin", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": false, "src_path": "source/foo.bin", "dest_path": ""}
  {"event_type": "closed", "is_directory": false, "src_path": "source/foo.bin", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
    """
    # WHEN
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()
    assert (target.target / 'foo.bin').read_bytes() == invalid_utf8


def test_rename_file(target):
    target.skip_for(sync_delta, 'not implemented')
    # GIVEN
    (target.source / 'foo.txt').write_text('content1')
    target.copy_source_to_target()
    # target.start()

    # WHEN
    (target.source / 'foo.txt').rename(target.source / 'bar.txt')
    # target.wait_at_rest()
    events = """
  {"event_type": "moved", "is_directory": false, "src_path": "source/foo.txt", "dest_path": "source/bar.txt"}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
"""
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert not (target.target / 'foo.txt').exists(), target.sync_error()
    assert (target.target / 'bar.txt').exists(), target.sync_error()
    assert (target.target / 'bar.txt').read_text() == 'content1'


def test_rename_folder(target):
    target.skip_for(sync_delta, 'not implemented')
    # GIVEN
    (target.source / 'sub1').mkdir()
    (target.source / 'sub1/foo.txt').write_text('content1')
    target.copy_source_to_target()
    # target.start()

    # WHEN
    (target.source / 'sub1').rename(target.source / 'sub2')
    # target.wait_at_rest()
    events = """
  {"event_type": "moved", "is_directory": true, "src_path": "source/sub1", "dest_path": "source/sub2"}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "moved", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": "source/sub2/foo.txt"}
"""
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()


def test_move_folder_in_subfolder(target):
    target.skip_for(sync_delta, 'not implemented')
    # GIVEN
    (target.source / 'sub1').mkdir()
    (target.source / 'sub1/foo.txt').write_text('content1')
    (target.source / 'sub2').mkdir()
    target.copy_source_to_target()
    # target.start()

    # WHEN
    shutil.move(str(target.source / 'sub1'), str(target.source / 'sub2/'))
    # target.wait_at_rest()
    events = """
  {"event_type": "moved", "is_directory": true, "src_path": "source/sub1", "dest_path": "source/sub2/sub1"}
  {"event_type": "modified", "is_directory": true, "src_path": "source", "dest_path": ""}
  {"event_type": "modified", "is_directory": true, "src_path": "source/sub2", "dest_path": ""}
  {"event_type": "moved", "is_directory": false, "src_path": "source/sub1/foo.txt", "dest_path": "source/sub2/sub1/foo.txt"}
"""
    # target.do_sync()
    target.apply_events(events)

    # THEN
    assert target.synchronized(), target.sync_error()
