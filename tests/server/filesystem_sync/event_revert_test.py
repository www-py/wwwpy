import pytest
from pathlib import Path
from dataclasses import dataclass

from wwwpy.common.filesystem.sync import Event
from wwwpy.server.filesystem_sync.event_revert import event_revert


def test_revert_create_file(tmp_path: Path):
    file_path = tmp_path / 'test_file.txt'
    file_path.touch()
    event = Event('created', False, 'test_file.txt')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert not (result / 'test_file.txt').exists()


def test_revert_create_directory(tmp_path: Path):
    dir_path = tmp_path / 'test_dir'
    dir_path.mkdir()
    event = Event('created', True, 'test_dir')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert not (result / 'test_dir').exists()


def test_revert_delete_file(tmp_path: Path):
    event = Event('deleted', False, 'deleted_file.txt')
    file_contents = {'deleted_file.txt': 'Original content'}
    result = event_revert(tmp_path, event, file_contents)
    assert (result / 'deleted_file.txt').is_file()
    assert (result / 'deleted_file.txt').read_text() == 'Original content'


def test_revert_delete_directory(tmp_path: Path):
    event = Event('deleted', True, 'deleted_dir')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert (result / 'deleted_dir').is_dir()


def test_revert_modify_file(tmp_path: Path):
    file_path = tmp_path / 'modified_file.txt'
    file_path.write_text('Modified content')
    event = Event('modified', False, 'modified_file.txt')
    file_contents = {'modified_file.txt': 'Original content'}
    result = event_revert(tmp_path, event, file_contents)
    assert (result / 'modified_file.txt').read_text() == 'Original content'


def test_revert_modify_file_no_content(tmp_path: Path):
    file_path = tmp_path / 'modified_file.txt'
    file_path.write_text('Modified content')
    event = Event('modified', False, 'modified_file.txt')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert (result / 'modified_file.txt').read_text() == ''


def test_revert_move_file(tmp_path: Path):
    dest_path = tmp_path / 'moved_file.txt'
    dest_path.touch()
    event = Event('moved', False, 'original_file.txt', 'moved_file.txt')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert not (result / 'moved_file.txt').exists()
    assert (result / 'original_file.txt').is_file()


def test_revert_move_directory(tmp_path: Path):
    dest_path = tmp_path / 'moved_dir'
    dest_path.mkdir()
    (dest_path / 'test_file.txt').touch()
    event = Event('moved', True, 'original_dir', 'moved_dir')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert not (result / 'moved_dir').exists()
    assert (result / 'original_dir').is_dir()
    assert (result / 'original_dir' / 'test_file.txt').is_file()


def test_revert_closed_event(tmp_path: Path):
    file_path = tmp_path / 'closed_file.txt'
    file_path.touch()
    initial_mtime = file_path.stat().st_mtime
    event = Event('closed', False, 'closed_file.txt')
    file_contents = {}
    result = event_revert(tmp_path, event, file_contents)
    assert (result / 'closed_file.txt').exists()
    assert (result / 'closed_file.txt').stat().st_mtime == initial_mtime
