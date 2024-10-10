from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import List

from watchdog.events import FileSystemEvent

from tests import timeout_multiplier
from wwwpy.server.filesystem_sync.any_observer import AnyObserver
from wwwpy.server.filesystem_sync import any_observer


any_observer.logger.setLevel('DEBUG')

def test_watch_non_existing_folder__should_not_fail(tmp_path):
    target = AnyObserver(tmp_path / 'folder1', lambda e: None)
    target.watch_directory()


def test_watch_existing_folder_should_yield_some_events(tmp_path: Path):
    # GIVEN
    events = []

    def callback(event: FileSystemEvent):
        events.append(event)

    target = AnyObserver(tmp_path, callback)
    target.watch_directory()

    # WHEN
    file_path = tmp_path / 'test_file.txt'
    file_path.touch()

    # THEN
    _assert_retry(lambda: len(events) > 0)


def test_non_existing_folder_than_created_should_yield_some_events(tmp_path: Path):
    # GIVEN
    events = []

    def callback(event: FileSystemEvent):
        events.append(event)

    folder1 = tmp_path / 'folder1'
    target = AnyObserver(folder1, callback)
    target.watch_directory()

    # WHEN
    # at this point, we are in polling mode, so we need a delay to wait for the AnyObserver to start
    folder1.mkdir()
    _assert_retry(lambda: target.active)
    (folder1 / 'file1.txt').touch()

    # WHEN
    _assert_retry(lambda: len(events) > 0)


def _assert_retry(condition):
    __tracebackhide__ = True
    [sleep(0.1) for _ in range(5 * timeout_multiplier()) if not condition()]
    assert condition(), 'wait_condition timeout'
