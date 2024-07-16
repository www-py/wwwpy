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

    def __str__(self):
        # on GitHub Actions when a test fails we can see the print of the variables in the local scope
        events_str = ', '.join([f"{event[1].event_type} at {event[1].src_path} after {event[0].total_seconds()} seconds" for event in self.events])
        return f"WatcherMock(tmp_path={self.tmp_path}, prev={self.prev}, events=[{events_str}])"

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


def test_watcher_delete(watcher_mock):
    file = watcher_mock.tmp_path / 'file.txt'
    file.write_text('world')

    watcher_mock.target.watch_directory()

    file.unlink()

    watcher_mock.wait_for_events(1)

    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0][1]
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'deleted'
