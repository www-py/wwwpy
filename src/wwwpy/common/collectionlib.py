from __future__ import annotations

from typing import Callable, TypeVar, Any

T = TypeVar('T')


# def _modify_method(f, which_arg=0, takes_list=False):
#     def new_f(*args):
#         if takes_list:
#             map(check_float, args[which_arg + 1])
#         else:
#             check_float(args[which_arg + 1])
#         return f(*args)
#     return new_f

class ListMap(list[T]):
    def __init__(self, *args: T, key_func: Callable[[T], Any] = None):
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
    def _key(self, item: T) -> Any:
        raise NotImplementedError

    def append(self, value: T):
        self._map[self._key(value)] = value
        super().append(value)

    def get(self, key) -> T | None:
        """Return the item with the given key or None if it does not exist."""
        return self._map.get(key)
