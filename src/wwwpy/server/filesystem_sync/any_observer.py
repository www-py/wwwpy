from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer


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
            pass # catch if it was not started

    def on_any_event(self, event: FileSystemEvent) -> None:
        self._callback(event)
