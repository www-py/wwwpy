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
