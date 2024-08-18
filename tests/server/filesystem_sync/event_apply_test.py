from wwwpy.common.filesystem.sync import Event
from wwwpy.common.filesystem.sync.event_apply import event_apply


def test_create_file(tmp_path):
    event = Event('created', False, 'test_file.txt')
    result = event_apply(tmp_path, event)
    assert (result / 'test_file.txt').is_file()


def test_create_directory(tmp_path):
    event = Event('created', True, 'test_dir')
    result = event_apply(tmp_path, event)
    assert (result / 'test_dir').is_dir()


def test_delete_file(tmp_path):
    file_path = tmp_path / 'to_delete.txt'
    file_path.touch()
    event = Event('deleted', False, 'to_delete.txt')
    result = event_apply(tmp_path, event)
    assert not (result / 'to_delete.txt').exists()


def test_delete_directory(tmp_path):
    dir_path = tmp_path / 'to_delete_dir'
    dir_path.mkdir()
    event = Event('deleted', True, 'to_delete_dir')
    result = event_apply(tmp_path, event)
    assert not (result / 'to_delete_dir').exists()


def test_modify_file(tmp_path):
    file_path = tmp_path / 'to_modify.txt'
    file_path.write_text("Original content")
    event = Event('modified', False, 'to_modify.txt')
    result = event_apply(tmp_path, event)
    assert (result / 'to_modify.txt').read_text() != "Original content"


def test_move_file(tmp_path):
    file_path = tmp_path / 'to_move.txt'
    file_path.touch()
    event = Event('moved', False, 'to_move.txt', 'moved.txt')
    result = event_apply(tmp_path, event)
    assert not (result / 'to_move.txt').exists()
    assert (result / 'moved.txt').is_file()


def test_move_directory(tmp_path):
    dir_path = tmp_path / 'to_move_dir'
    dir_path.mkdir()
    event = Event('moved', True, 'to_move_dir', 'moved_dir')
    result = event_apply(tmp_path, event)
    assert not (result / 'to_move_dir').exists()
    assert (result / 'moved_dir').is_dir()


def test_closed_event(tmp_path):
    file_path = tmp_path / 'closed_file.txt'
    file_path.touch()
    initial_mtime = file_path.stat().st_mtime
    event = Event('closed', False, 'closed_file.txt')
    result = event_apply(tmp_path, event)
    assert (result / 'closed_file.txt').exists()
    assert (result / 'closed_file.txt').stat().st_mtime == initial_mtime
