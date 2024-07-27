from datetime import datetime
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent, DirModifiedEvent
from watchdog.observers import Observer

from wwwpy.common.throttler import Event
from wwwpy.server.throttler_thread import EventThrottlerThread


class ChangeHandler(FileSystemEventHandler):

    def __init__(self, path: Path, callback: Callable[[FileSystemEvent], None]):
        self._path = path
        self._callback = callback
        self._observer = Observer()

        def _emit(event: Event):
            self._callback(event.item)

        self._throttler = EventThrottlerThread(100, _emit, datetime.utcnow)
        super().__init__()

    def on_any_event(self, event: FileSystemEvent) -> None:
        if Path(event.src_path) == self._path:
            return
        if isinstance(event, DirModifiedEvent):
            return
        if event.event_type == 'closed' or event.event_type == 'opened' or event.event_type == 'created':
            return

        key = str(event.src_path)
        if key.endswith('.py~'):
            return
        self._throttler.new_event(Event(key, event))

    def watch_directory(self):
        self._observer.schedule(self, str(self._path), recursive=True)
        self._observer.start()

    def stop_join(self):
        self._observer.stop()
        self._observer.join()
