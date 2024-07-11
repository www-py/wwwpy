from datetime import datetime
from time import sleep

import pytest

from tests import timeout_multiplier
from wwwpy.common.event_observer import EventObserver
from wwwpy.server import watcher


class WatcherMock:
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.target = watcher.ChangeHandler(tmp_path, self.callback)
        self.prev = datetime.utcnow()
        self.events = []

    def callback(self, event):
        utcnow = datetime.utcnow()
        delta = utcnow - self.prev
        self.prev = utcnow
        self.events.append((delta, event))

    def wait_for_events(self, count):
        [sleep(0.1 * timeout_multiplier()) for _ in range(10) if len(self.events) < count]


@pytest.fixture
def watcher_mock(tmp_path):
    return WatcherMock(tmp_path)


def test_watcher_modify(watcher_mock):
    file = watcher_mock.tmp_path / 'file.txt'
    file.write_text('hello')

    watcher_mock.target.watch_directory()

    file.write_text('world')
    watcher_mock.wait_for_events(1)
    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0][1]
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'modified'


def test_watcher_new_file(watcher_mock):

    watcher_mock.target.watch_directory()

    file = watcher_mock.tmp_path / 'file.txt'
    file.write_text('world')
    watcher_mock.wait_for_events(1)

    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0][1]
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'modified'
