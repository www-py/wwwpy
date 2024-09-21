from dataclasses import dataclass
from typing import List

from wwwpy.common import property_monitor as pm
from wwwpy.common.property_monitor import PropertyChange, monitor_changes
import pytest


@dataclass
class TestClass:
    name: str = ""
    value: int = 0


def test_monitor_existing_property_change():
    events: List[List[PropertyChange]] = []

    def on_change(changes: List[PropertyChange]):
        events.append(changes)

    obj = TestClass("bob", 10)
    monitor_changes(obj, on_change)

    obj.value = 20

    assert events == [[PropertyChange(obj, "value", 10, 20)]]


def test_monitor_on_second_instance():
    events1: List[List[PropertyChange]] = []
    events2: List[List[PropertyChange]] = []

    def on_change1(changes: List[PropertyChange]):
        events1.append(changes)

    def on_change2(change2: List[PropertyChange]):
        events2.append(change2)

    obj1 = TestClass("alice", 10)
    monitor_changes(obj1, on_change1)
    obj2 = TestClass("bob", 20)
    monitor_changes(obj2, on_change2)

    obj1.value = 1

    assert events1 == [[PropertyChange(obj1, "value", 10, 1)]]
    assert events2 == []

    obj2.value = 2

    assert events1 == [[PropertyChange(obj1, "value", 10, 1)]]
    assert events2 == [[PropertyChange(obj2, "value", 20, 2)]]


def test_double_monitor__should_raise_exception():
    obj = TestClass("alice", 10)
    monitor_changes(obj, lambda change: None)
    with pytest.raises(Exception):
        monitor_changes(obj, lambda change: None)


def test_group_changes():
    events: List[List[PropertyChange]] = []

    def on_change(changes: List[PropertyChange]):
        events.append(changes)

    obj = TestClass("alice", 10)
    monitor_changes(obj, on_change)

    with pm.group_changes(obj):
        obj.value = 1
        assert events == []
        obj.name = "bob"
        assert events == []

    assert events == [[PropertyChange(obj, "value", 10, 1), PropertyChange(obj, "name", "alice", "bob")]]
    events.clear()

    # verify immediate delivery of changes
    obj.value = 123
    assert events == [[PropertyChange(obj, "value", 1, 123)]]
