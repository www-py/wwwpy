from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterator
from wwwpy.common import state


@dataclass
class State1:
    length: int = 0
    name: str = ""


def test_state():
    storage = state.DictStorage()
    restore = state.State(storage, 'state1').restore(State1)
    assert not restore.present


def test_save():
    storage = state.DictStorage()
    assert storage.length == 0

    instance = State1(length=1, name='test')
    state.State(storage, 'state1').save(instance)

    assert storage.length > 0


def test_save_and_restore():
    storage = state.DictStorage()

    instance = State1(length=1, name='test')
    state.State(storage, 'state1').save(instance)

    restore = state.State(storage, 'state1').restore(State1)

    assert restore.present
    assert restore.instance == instance
    assert restore.instance is not instance


def test_broken_restore():
    storage = state.DictStorage()
    storage.storage['state1'] = 'broken'

    restore = state.State(storage, 'state1').restore(State1)

    assert restore.present
    assert restore.exception is not None
    assert restore.instance is None


def test_broken_with_default():
    storage = state.DictStorage()
    storage.storage['state1'] = 'broken'

    restore = state.State(storage, 'state1').restore(State1)

    assert restore.present
    assert restore.instance is None
    assert restore.exception is not None
    assert restore.instance_or_default() == State1()


def test_not_broken_with_default():
    storage = state.DictStorage()

    instance = State1(length=1, name='test')
    state.State(storage, 'state1').save(instance)

    restore = state.State(storage, 'state1').restore(State1)

    default = restore.instance_or_default()
    assert default is restore.instance


class TestPersist:

    def test_persist(self):
        # GIVEN
        @dataclass
        class State:
            counter: int = 0

        storage = state.DictStorage()

        # WHEN
        target = state._restore(State, storage)
        target.counter = 1

        # THEN
        restore = state._restore(State, storage)
        assert restore.counter == 1
