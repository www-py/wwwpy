from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterator, TypeVar, Generic, Type

from wwwpy.common.rpc import serialization

import logging

logger = logging.getLogger(__name__)


def _restore(cls: Type[T], storage: Storage = None) -> T:
    if storage is None:
        storage = JsStorage()
    name = cls.__module__ + '.' + cls.__name__
    state_manager = State(storage, f'wwwpy.persist.{name}')
    result = state_manager.restore(cls).instance_or_default()

    def save():
        logger.debug(f'save {name} state res={result}')
        state_manager.save(result)

    from .property_monitor import monitor_changes
    monitor_changes(result, lambda *a: save())
    return result


class Storage(Protocol):
    @property
    def length(self) -> int: ...

    def keys(self) -> Iterator[str]: ...

    def items(self) -> Iterator[tuple[str, str]]: ...

    def getItem(self, key: str) -> str | None: ...

    def setItem(self, key: str, value: str): ...

    def removeItem(self, key: str): ...


T = TypeVar('T')


@dataclass
class Restore(Generic[T]):
    clazz: Type[T]
    present: bool
    instance: T | None
    exception: Exception | None = None

    def instance_or_default(self) -> T:
        return self.instance if self.instance else self.clazz()


class State:
    def __init__(self, storage: Storage, key: str):
        self.key = key
        self.storage = storage

    def restore(self, clazz: Type[T]) -> Restore[T]:
        j = self.storage.getItem(self.key)
        if not j:
            return Restore(clazz, False, None)
        try:
            obj = serialization.from_json(j, clazz)
        except Exception as e:
            logger.error(f'failed restore of type {clazz} with json ```{j}```')
            import traceback
            traceback.print_exc()
            return Restore(clazz, True, None, e)
        return Restore(clazz, True, obj)

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
