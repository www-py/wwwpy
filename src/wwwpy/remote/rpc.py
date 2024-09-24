from typing import Protocol, List, Any


class FileChangedListener(Protocol):
    def __call__(self, package: str, events: List[Any]):
        ...


_file_changed_listeners: List[FileChangedListener] = []


class BrowserRpc:

    def package_file_changed_sync(self, package: str, events: List[Any]):
        for listener in _file_changed_listeners:
            listener(package, events)


def file_changed_listeners_add(listener: FileChangedListener):
    _file_changed_listeners.append(listener)
