from pathlib import Path
from threading import Thread
from time import sleep
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from wwwpy.common.filesystem.sync import new_tmp_path

import logging

logger = logging.getLogger(__name__)


class AnyObserver(FileSystemEventHandler):

    def __init__(self, path: Path, callback: Callable[[FileSystemEvent], None]):
        """path need to exist, otherwise the observer will throw an exception."""
        self._path = path
        self._callback = callback
        self._observer = None
        super().__init__()

    def watch_directory(self):
        if self._path.exists():
            self._new_observer()
        else:
            logger.debug(f'path does not exist, waiting for it to be created: {self._path}')
            Thread(target=self._wait_for_path, daemon=True).start()

    @property
    def active(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

    def _wait_for_path(self):
        while not self._path.exists():
            sleep(0.1)
        self._new_observer()

    def _new_observer(self):
        logger.debug(f'Creating observer for {self._path}')
        self._observer = Observer()
        self._observer.schedule(self, str(self._path), recursive=True)
        self._observer.start()

    def stop(self):
        self._observer.stop()

    def join(self):
        try:
            self._observer.join()
        except RuntimeError:
            pass  # catch if it was not started

    def on_any_event(self, event: FileSystemEvent) -> None:
        if not Path(event.src_path).is_relative_to(self._path):
            return
        if self._is_self_delete(event):
            self._observer.stop()
            self._observer = None
            self._wait_for_path()
            return

        self._callback(event)

    def _is_self_delete(self, event: FileSystemEvent) -> bool:
        return event.event_type == 'deleted' and Path(event.src_path) == self._path


def main():
    tmp_path = new_tmp_path()
    print(f'watching {tmp_path}')

    def print_event(event: FileSystemEvent):
        print(f'{event}')

    AnyObserver(tmp_path, print_event).watch_directory()

    while True:
        sleep(1)


if __name__ == '__main__':
    main()
