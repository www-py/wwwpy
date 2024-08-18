from pathlib import Path
from time import sleep
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from wwwpy.common.filesystem.sync import new_tmp_path


class AnyObserver(FileSystemEventHandler):

    def __init__(self, path: Path, callback: Callable[[FileSystemEvent], None]):
        """path need to exist, otherwise the observer will throw an exception."""
        self._path = path
        self._callback = callback
        self._observer = Observer()
        super().__init__()

    def watch_directory(self):
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
        self._callback(event)


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
