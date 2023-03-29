from typing import Iterable, TypeVar, Generic, Callable, Iterator

_T = TypeVar('_T')


class repeatable_chain:
    def __init__(self, *iterables: Iterable[_T]):
        self._iterables = iterables

    def __iter__(self) -> Iterable[_T]:
        def it() -> Iterable[_T]:
            for iterable in self._iterables:
                yield from iterable

        return it()


class CallableToIterable(Generic[_T]):
    def __init__(self, iterator_factory: Callable[[], Iterator[_T]]):
        self.iterator_factory = iterator_factory

    def __iter__(self) -> Iterator[_T]:
        return self.iterator_factory()
