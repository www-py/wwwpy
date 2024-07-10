from typing import Callable, Protocol, List

from js import document, console


class FileChangedListener(Protocol):
    def __call__(self, filename: str, content: str):
        ...


_listeners: List[FileChangedListener] = []


class BrowserRpc:

    def file_changed(self, filename: str, content: str):
        console.log(f'file_changed123: {filename}')
        for listener in _listeners:
            listener(filename, content)


def add_listener(listener: FileChangedListener):
    _listeners.append(listener)
