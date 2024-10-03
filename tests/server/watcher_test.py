import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
import datetime as datetime_module
from pathlib import Path
from time import sleep
from typing import List

import pytest
from watchdog.events import FileSystemEvent

from tests import timeout_multiplier
from wwwpy.server import watcher


@dataclass()
class MockEvent:
    arrival: datetime
    delta: timedelta
    event: FileSystemEvent


class WatcherMock:
    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path
        self.target = watcher.ChangeHandler(tmp_path, self.callback)
        self.prev = datetime.utcnow()
        self.events: List[MockEvent] = []

    def callback(self, event):
        arrival = datetime.utcnow()
        delta = arrival - self.prev
        self.prev = arrival
        mock_event = MockEvent(arrival, delta, event)
        self.events.append(mock_event)
        print(f"WatcherMock.callback: {mock_event}")

    def wait_for_events(self, count):
        start = datetime.utcnow()
        [sleep(0.1 * timeout_multiplier()) for _ in range(10) if len(self.events) < count]
        if len(self.events) < count:
            delta = datetime.utcnow() - start
            raise print(f"wait_for_events, expected {count} events, got {len(self.events)} delta={delta}",
                        file=sys.stderr)

    def __str__(self):
        # on GitHub Actions when a test fails we can see the print of the variables in the local scope
        events_str = ', '.join([
            f"arrival:{event.arrival} delta:{event.delta} {event.event.event_type} at {event.event.src_path}"
            for event in self.events])
        return f"WatcherMock(tmp_path={self.tmp_path}, prev={self.prev}, events=[{events_str}])"

    def __repr__(self):
        return str(self)


@pytest.fixture
def watcher_mock(tmp_path):
    return WatcherMock(tmp_path)


def test_watcher__unmonitored_folder(watcher_mock):
    watcher_mock.target.watch_directory()
    (watcher_mock.tmp_path / 'unmonitored').mkdir()
    watcher_mock.wait_for_events(0)
    assert watcher_mock.events == []


def test_watcher__common_should_be_monitored(watcher_mock):
    common = watcher_mock.tmp_path / 'common'
    common.mkdir()
    watcher_mock.target.watch_directory()
    (common / 'hello.py').write_text('hello')
    watcher_mock.wait_for_events(1)
    assert len(watcher_mock.events) == 1


def test_watcher_modify(watcher_mock):
    file = watcher_mock.tmp_path / 'common' / 'file.txt'
    file.parent.mkdir()
    file.write_text('hello')

    watcher_mock.target.watch_directory()

    file.write_text('world')
    watcher_mock.wait_for_events(1)
    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0].event
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'modified'


def test_watcher_new_file(watcher_mock):
    watcher_mock.target.watch_directory()

    file = watcher_mock.tmp_path / 'common/file.txt'
    file.parent.mkdir()
    file.write_text('world')
    watcher_mock.wait_for_events(1)

    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0].event
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'modified'


def test_watcher_delete(watcher_mock):
    file = watcher_mock.tmp_path / 'common' / 'file.txt'
    file.parent.mkdir()
    file.write_text('world')

    watcher_mock.target.watch_directory()

    file.unlink()

    watcher_mock.wait_for_events(1)

    assert len(watcher_mock.events) == 1
    fs_event = watcher_mock.events[0].event
    assert fs_event.src_path == str(file)
    assert fs_event.event_type == 'deleted'
