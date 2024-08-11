import filecmp
import json
import shutil
import sys
from datetime import timedelta
from pathlib import Path
from threading import Lock
from time import sleep
from typing import List

import pytest
from watchdog.events import FileSystemEvent

from tests import timeout_multiplier
from tests.server.filesystem_sync.activity_monitor import ActivityMonitor
from wwwpy.server.filesystem_sync import filesystemevents_print, Sync, new_tmp_path
from wwwpy.server.filesystem_sync import sync_delta, sync_zip
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer


class SyncFixture:

    def __init__(self, tmp_path: Path, exist_ok=False, print_changes=True, sync: Sync = sync_delta):
        self.sync = sync
        self.print_changes = print_changes
        self.source = tmp_path / 'source'
        self.source.mkdir(exist_ok=exist_ok)
        self.target = tmp_path / 'target'
        self.target.mkdir(exist_ok=exist_ok)
        self.all_events = []
        self.window = timedelta(milliseconds=100 * timeout_multiplier())
        self.activities = ActivityMonitor(self.window + timedelta(milliseconds=10 * timeout_multiplier()))
        self.dircmp = None
        self._lock = Lock()
        self.callback_count = 0

        self.debounced_watcher = None

        self.activities.touch()

    def start(self):

        def callback(events: List[FileSystemEvent]):
            self.callback_count += 1
            filesystemevents_print(events)
            self.activities.touch()
            with self._lock:
                self.all_events.extend(events)

        self.debounced_watcher = WatchdogDebouncer(self.source, self.window, callback)
        self.debounced_watcher.start()

    def wait_at_rest(self):
        [sleep(0.1) for _ in range(40 * timeout_multiplier()) if not self.activities.at_rest()]
        assert self.activities.at_rest(), self.activities.rest_delta()

    def do_sync(self):
        changes = self.get_changes()
        self.apply_changes(changes)
        return changes

    def apply_changes(self, changes):
        self.sync.sync_target(self.target, json.loads(json.dumps(changes)))

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
        self._calc_synchronized()
        return self._is_synchronized()

    def _is_synchronized(self) -> bool:
        return not self.dircmp.left_only and not self.dircmp.right_only and not self.dircmp.diff_files

    def _calc_synchronized(self):
        self.dircmp = filecmp.dircmp(self.source, self.target)

    def sync_error(self):
        def diff_printable():
            return f'source_only={self.dircmp.left_only} target_only={self.dircmp.right_only} diff_files={self.dircmp.diff_files}'

        return None if self._is_synchronized() else diff_printable()

    def copy_source_to_target(self):
        shutil.rmtree(self.target, ignore_errors=True)
        shutil.copytree(self.source, self.target, dirs_exist_ok=True)

    def skip_for(self, sync, reason):
        if self.sync == sync:
            pytest.skip(f'Skipped for {sync} {reason}')


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
