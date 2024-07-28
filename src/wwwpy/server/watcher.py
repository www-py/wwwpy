from datetime import datetime
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler, FileSystemEvent, DirModifiedEvent
from watchdog.observers import Observer

from wwwpy.common.throttler import Event
from wwwpy.server.throttler_thread import EventThrottlerThread

_default_folders = {'remote', 'common'}


class ChangeHandler(FileSystemEventHandler):

    def __init__(self, path: Path, callback: Callable[[FileSystemEvent], None], folders: set[str] = _default_folders):
        """path need to exist, otherwise the observer will throw an exception. Path should be the root of wwwpy working dir.
        folders is a set of folder names (children of path) that are monitored for changes.
        """
        self._path = path
        self._callback = callback
        self._folders = map(lambda f: path / f, folders)
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
        src_path = Path(event.src_path)
        rel = src_path.relative_to(self._path)
        if rel.parts[0] not in _default_folders:
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
