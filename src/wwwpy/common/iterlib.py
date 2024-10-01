from typing import Iterable, TypeVar, Generic, Callable, Iterator

_T = TypeVar('_T')


class repeatable_chain(Generic[_T]):
    def __init__(self, *iterables: Iterable[_T]):
        self._iterables = iterables

    def __iter__(self) -> Iterator[_T]:
        def it() -> Iterator[_T]:
            for iterable in self._iterables:
                yield from iterable

        return it()


class CallableToIterable(Generic[_T]):
    def __init__(self, iterator_factory: Callable[[], Iterator[_T]]):
        self.iterator_factory = iterator_factory

    def __iter__(self) -> Iterator[_T]:
        try:
            return iter_catching(self.iterator_factory())
        except:
            import traceback
            traceback.print_exc()
            return iter([])


def iter_catching(gen):
    while True:
        try:
            yield next(gen)
        except StopIteration:
            break
        except Exception as e:
            import traceback
            traceback.print_exc()
