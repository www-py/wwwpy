import os
from typing import Dict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from pathlib import Path
import time
from datetime import datetime


class _ChangeHandler(FileSystemEventHandler):

    def __init__(self, path: Path, callback):
        self.path = path
        self.callback = callback
        self.observer = Observer()
        super().__init__()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.event_type != 'modified':
            return

        dt = datetime.now()
        print(f'{dt} Event: {event.event_type} Path: {event.src_path}')

        self.callback(event.src_path)

    def watch_directory(self):
        self.observer.schedule(self, str(self.path), recursive=True)
        self.observer.start()

    def stop_join(self):
        self.observer.stop()
        self.observer.join()


def _watch_directory(path: Path, callback):
    handler = _ChangeHandler(path, callback)
    handler.watch_directory()
