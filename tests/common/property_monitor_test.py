from dataclasses import dataclass
from typing import List

from wwwpy.common import property_monitor as pm
from wwwpy.common.property_monitor import PropertyChange, monitor_property_changes
import pytest


@dataclass
class TestClass:
    name: str = ""
    value: int = 0


def test_monitor_existing_property_change():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        changes.append(change)

    obj = TestClass("bob", 10)
    monitor_property_changes(obj, on_change)

    obj.value = 20

    assert changes == [PropertyChange(obj, "value", 10, 20)]


def test_monitor_on_second_instance():
    changes1: List[PropertyChange] = []
    changes2: List[PropertyChange] = []

    def on_change1(change: PropertyChange):
        changes1.append(change)

    def on_change2(change: PropertyChange):
        changes2.append(change)

    obj1 = TestClass("alice", 10)
    monitor_property_changes(obj1, on_change1)
    obj2 = TestClass("bob", 20)
    monitor_property_changes(obj2, on_change2)

    obj1.value = 1

    assert changes1 == [PropertyChange(obj1, "value", 10, 1)]
    assert changes2 == []

    obj2.value = 2

    assert changes1 == [PropertyChange(obj1, "value", 10, 1)]
    assert changes2 == [PropertyChange(obj2, "value", 20, 2)]


def test_double_monitor__should_raise_exception():
    obj = TestClass("alice", 10)
    monitor_property_changes(obj, lambda change: None)
    with pytest.raises(Exception):
        monitor_property_changes(obj, lambda change: None)


def main():
    obj = TestClass(value=10)

    def on_change(change: pm.PropertyChange):
        print(f"Change detected: {change.name} from {change.old_value} to {change.new_value}")

    pm.monitor_property_changes(obj, on_change=on_change)
    obj.value = 20
    obj.name = "John"
    obj.new_prop = "new"
    obj.new_prop = "new2"


if __name__ == '__main__':
    main()
