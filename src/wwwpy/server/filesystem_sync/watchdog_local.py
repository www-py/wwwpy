import shutil
import sys
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import List

from wwwpy.server.filesystem_sync import new_tmp_path, filesystemevents_print, Sync
from wwwpy.server.filesystem_sync import sync_zip
from wwwpy.common.filesystem.sync.event import Event
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer


class WatchdogLocal:
    def __init__(self, tmp_path: Path, sync: Sync, exist_ok=False, print_changes=True):
        self.sync = sync
        self.source = tmp_path / 'source'
        self.source.mkdir(exist_ok=exist_ok)
        self.target = tmp_path / 'target'
        self.target.mkdir(exist_ok=exist_ok)
        self.window = timedelta(milliseconds=100)
        self.callback_count = 0

        def callback(events: List[Event]):
            assert events
            self.callback_count += 1
            filesystemevents_print(events)
            changes = self.sync.sync_source(self.source, events)
            self.sync.sync_target(self.target, changes)

        self.debounced_watcher = WatchdogDebouncer(self.source, self.window, callback)

    def start(self):
        self.debounced_watcher.start()

    def copy_source_to_target(self):
        shutil.rmtree(self.target, ignore_errors=True)
        shutil.copytree(self.source, self.target, dirs_exist_ok=True)

def main():
    tmp_path = Path(sys.argv[1]) if len(sys.argv) > 1 else new_tmp_path()

    local = WatchdogLocal(tmp_path, exist_ok=True, sync=sync_zip)
    local.copy_source_to_target()

    print(f'watching file://{local.source}')
    local.start()
    while True:
        sleep(10)


if __name__ == '__main__':
    main()
