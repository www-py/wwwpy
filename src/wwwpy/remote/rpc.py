from typing import Protocol, List


class FileChangedListener(Protocol):
    def __call__(self, event_type: str, filename: str, content: str):
        ...


_file_changed_listeners: List[FileChangedListener] = []


class BrowserRpc:

    def file_changed(self, event_type: str, filename: str, content: str):
        for listener in _file_changed_listeners:
            listener(event_type, filename, content)


def file_changed_listeners_add(listener: FileChangedListener):
    _file_changed_listeners.append(listener)
