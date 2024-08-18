from typing import Protocol, List, Any


class FileChangedListener(Protocol):
    def __call__(self, events: List[Any]):
        ...


_file_changed_listeners: List[FileChangedListener] = []


class BrowserRpc:

    def file_changed_sync(self, events: List[Any]):
        for listener in _file_changed_listeners:
            listener(events)


def file_changed_listeners_add(listener: FileChangedListener):
    _file_changed_listeners.append(listener)
