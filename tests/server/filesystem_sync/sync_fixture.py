import dataclasses
import json
import shutil
import sys
from datetime import timedelta
from pathlib import Path
from threading import Lock
from time import sleep
from typing import List

import pytest

from tests import timeout_multiplier
from tests.server.filesystem_sync.activity_monitor import ActivityMonitor
from tests.server.filesystem_sync.fs_compare import FsCompare
from wwwpy.common.rpc import serialization
from wwwpy.server.filesystem_sync import Sync, new_tmp_path, Event
from wwwpy.server.filesystem_sync import sync_delta, sync_zip
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer


class SyncFixture:

    def __init__(self, tmp_path: Path, exist_ok=False, print_changes=True, sync: Sync = sync_delta):
        self.sync = sync
        self.print_changes = print_changes
        self.tmp_path = tmp_path
        self.source = tmp_path / 'source'
        self.source.mkdir(exist_ok=exist_ok)
        self.target = tmp_path / 'target'
        self.target.mkdir(exist_ok=exist_ok)
        self.all_events = []
        self.window = timedelta(milliseconds=100 * timeout_multiplier())
        self.activities = ActivityMonitor(self.window + timedelta(milliseconds=10 * timeout_multiplier()))
        self.fs_compare = FsCompare(self.source, self.target, 'source', 'target')
        self._lock = Lock()
        self.callback_count = 0

        def callback(events: List[Event]):
            self.callback_count += 1
            _events_serialize_print(events, tmp_path)
            self.activities.touch()
            with self._lock:
                self.all_events.extend(events)

        self.debounced_watcher = WatchdogDebouncer(self.source, self.window, callback)

        self.activities.touch()

    def start(self):
        self.debounced_watcher.start()

    def wait_at_rest(self):
        [sleep(0.1) for _ in range(40 * timeout_multiplier()) if not self.activities.at_rest()]
        assert self.activities.at_rest(), self.activities.rest_delta()

    def do_sync(self):
        changes = self.get_changes()
        self.apply_changes(changes)
        return changes

    def apply_changes(self, changes):
        dumps = json.dumps(changes)
        loads = json.loads(dumps)
        self.sync.sync_target(self.target, loads)

    def get_changes(self):
        with self._lock:
            all_events = self.all_events.copy()
            self.all_events.clear()

        changes = self.sync.sync_source(self.source, all_events)
        dumps = json.dumps(changes)
        if self.print_changes and len(changes) > 0:
            print(f'\ndumps=```{dumps}```')
        return changes

    def do_init(self):
        self.apply_changes(self.sync.sync_init(self.source))

    def synchronized(self):
        return self.fs_compare.synchronized()

    def sync_error(self):
        return self.fs_compare.sync_error()

    def copy_source_to_target(self):
        shutil.rmtree(self.target, ignore_errors=True)
        shutil.copytree(self.source, self.target, dirs_exist_ok=True)

    def skip_for(self, sync, reason):
        if self.sync == sync:
            pytest.skip(f'Skipped for {sync} {reason}')

    def apply_events(self, events_str: str):
        events = _deserialize_events(events_str)

        def relocate(e: Event) -> Event:
            src_path = '' if e.src_path == '' else str(self.tmp_path / e.src_path)
            dest_path = '' if e.dest_path == '' else str(self.tmp_path / e.dest_path)
            return dataclasses.replace(e, src_path=src_path, dest_path=dest_path)

        events_fix = [relocate(e) for e in events]
        with self._lock:
            self.all_events.extend(events_fix)
        return self.do_sync()


def _events_serialize_print(events: List[Event], tmp_path):
    for e in events:
        ser = serialization.to_json(e, Event)
        ser2 = ser.replace(str(tmp_path) + '/', '')
        print(f'  {ser2}')
    print(f'FileSystemEvent serialized: {len(events)}')


def _deserialize_events(events: str) -> List[Event]:
    result = []
    for line in events.split('\n'):
        line = line.strip()
        if not line:
            continue
        event = serialization.from_json(line, Event)
        result.append(event)
    return result


def main():
    tmp_path = Path(sys.argv[1]) if len(sys.argv) > 1 else new_tmp_path()
    fixture = SyncFixture(tmp_path, exist_ok=True, print_changes=False, sync=sync_zip)
    fixture.copy_source_to_target()
    fixture.start()
    print(f'Watching file://{fixture.source}')
    while True:
        fixture.wait_at_rest()
        changes = fixture.do_sync()
        if changes:
            print(f'Changes len: {len(changes)}')


if __name__ == '__main__':
    main()
