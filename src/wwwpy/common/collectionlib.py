from __future__ import annotations

from typing import Callable, TypeVar, Any, Generic, Collection

T = TypeVar('T')
K = TypeVar('K')


class ListMap(list[T]):
    def __init__(self, args: Collection[T] = (), key_func: Callable[[T], K] = None):
        super().__init__(args)
        if key_func is not None:
            self._key = key_func
        self._map = {self._key(item): item for item in self}

    # append = _modify_method(list.append)
    # extend = _modify_method(list.extend, takes_list=True)
    # insert = _modify_method(list.insert, 1)
    # __add__ = _modify_method(list.__add__, takes_list=True)
    # __iadd__ = _modify_method(list.__iadd__, takes_list=True)
    # __setitem__ = _modify_method(list.__setitem__, 1)
    def _key(self, item: T) -> K:
        return item

    def append(self, value: T):
        self._map[self._key(value)] = value
        super().append(value)

    def get(self, key: K) -> T | None:
        """Return the item with the given key or None if it does not exist."""
        return self._map.get(key)
