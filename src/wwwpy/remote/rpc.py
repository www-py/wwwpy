from typing import Protocol, List


class FileChangedListener(Protocol):
    def __call__(self, event_type: str, filename: str, content: str):
        ...


_listeners: List[FileChangedListener] = []


class BrowserRpc:

    def file_changed(self, event_type: str, filename: str, content: str):
        for listener in _listeners:
            listener(event_type, filename, content)


def add_listener(listener: FileChangedListener):
    _listeners.append(listener)
