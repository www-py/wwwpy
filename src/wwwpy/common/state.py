from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterator

from wwwpy.common.rpc import serialization


class Storage(Protocol):
    @property
    def length(self) -> int: ...

    def keys(self) -> Iterator[str]: ...

    def items(self) -> Iterator[tuple[str, str]]: ...

    def getItem(self, key: str) -> str | None: ...

    def setItem(self, key: str, value: str): ...

    def removeItem(self, key: str): ...


@dataclass
class Restore:
    present: bool
    instance: any


class State:
    def __init__(self, storage: Storage, key: str):
        self.key = key
        self.storage = storage

    def restore(self, clazz) -> Restore:
        j = self.storage.getItem(self.key)
        if not j:
            return Restore(False, None)

        obj = serialization.from_json(j, clazz)
        return Restore(True, obj)

    def save(self, obj):
        j = serialization.to_json(obj, type(obj))
        self.storage.setItem(self.key, j)


class DictStorage(Storage):

    def __init__(self):
        self.storage = {}

    def keys(self) -> Iterator[str]:
        return iter(self.storage.keys())

    @property
    def length(self) -> int:
        return len(self.storage)

    def items(self) -> Iterator[tuple[str, str]]:
        return iter(self.storage.items())

    def getItem(self, key: str) -> str | None:
        return self.storage.get(key)

    def setItem(self, key: str, value: str):
        self.storage[key] = value

    def removeItem(self, key: str):
        del self.storage[key]


class JsStorage(Storage):
    def __init__(self, js_storage=None):
        if js_storage is None:
            import js
            js_storage = js.window.localStorage
        self.storage = js_storage

    def keys(self) -> Iterator[str]:
        for i in range(self.storage.length):
            yield self.storage.key(i)

    @property
    def length(self) -> int:
        return self.storage.length

    def items(self) -> Iterator[tuple[str, str]]:
        return self.storage.items()

    def getItem(self, key: str) -> str | None:
        return self.storage.getItem(key)

    def setItem(self, key: str, value: str):
        self.storage.setItem(key, value)

    def removeItem(self, key: str):
        self.storage.removeItem(key)
