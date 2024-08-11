import threading
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import Callable, List

from watchdog.events import FileSystemEvent

from wwwpy.server.filesystem_sync import new_tmp_path
from wwwpy.server.filesystem_sync.any_observer import AnyObserver
from wwwpy.server.filesystem_sync.debouncer import Debouncer
from wwwpy.server.filesystem_sync.debouncer_thread import DebouncerThread


class WatchdogDebouncer(DebouncerThread):

    def __init__(self, path: Path, window: timedelta, callback: Callable[[List[FileSystemEvent]], None]):
        self._debouncer = Debouncer(window)
        super().__init__(self._debouncer, callback)

        def skip_open(event: FileSystemEvent):
            if event.event_type != 'opened':
                self._debouncer.add_event(event)

        self._any_observer = AnyObserver(path, skip_open)

    def start(self):
        self._any_observer.watch_directory()
        super().start()

    def stop(self):
        self._any_observer.stop()
        super().stop()

    def join(self):
        self._any_observer.join()
        super().join()


def main():
    tmp_path = new_tmp_path()

    def print_events(events: List[FileSystemEvent]):
        print('=' * 20 + f' current thread name={threading.current_thread().name}')
        print(f'len={len(events)} events={events}')

    WatchdogDebouncer(tmp_path, timedelta(milliseconds=100), print_events).start()

    counter = 0

    def send(n, between, final):
        nonlocal counter
        counter += 1
        for _ in range(n, ):
            (tmp_path / f"e{counter}.txt").write_text(f"e{counter}")
            sleep(between)
        sleep(final)

    send(1, 0.01, 1)
    send(10, 0.01, 1)

    sleep(3)
    return

    for t in range(10):
        send(5, 0.09, 1)
        send(100, 0.01, 0.3)
        send(10, 0.05, 0.5)


if __name__ == '__main__':
    main()
