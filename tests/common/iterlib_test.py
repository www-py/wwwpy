from typing import Iterable, TypeVar, Generic, Callable, Iterator

from wwwpy.common import iterlib


def test_callable_to_iterable():
    def call():
        yield 1
        yield 2

    target = iterlib.CallableToIterable(call)

    assert list(target) == [1, 2]
    assert list(target) == [1, 2]


def test_should_swallow_exception__during_creation():
    def call():
        raise Exception('some')

    target = iterlib.CallableToIterable(call)

    assert list(target) == []
    assert list(target) == []


def test_should_swallow_exception__during_iteration():
    def call():
        yield 1
        raise Exception('some')

    target = iterlib.CallableToIterable(call)

    assert list(target) == [1]
    assert list(target) == [1]
