from dataclasses import dataclass
from typing import Callable


@dataclass
class PropertyChange:
    instance: any
    name: str
    old_value: object
    new_value: object


def monitor_property_changes(instance, on_change: Callable[[PropertyChange], None]):
    """Monitor the changes of the properties of an instance of a class."""
    if hasattr(instance, "__attr_change_monitor_on_change"):
        raise Exception("The instance is already being monitored for property changes")

    clazz = instance.__class__
    if not hasattr(clazz, "__attr_change_monitor"):
        setattr(clazz, "__attr_change_monitor", True)

        original_setattr = clazz.__setattr__  # Keep a reference to the original method

        def new_setattr(self, name, value):
            if hasattr(self, name) and name != "__attr_change_monitor_on_change" and \
                    hasattr(self, "__attr_change_monitor_on_change"):
                change = PropertyChange(self, name, getattr(self, name), value)
                self.__attr_change_monitor_on_change(change)
            original_setattr(self, name, value)

        clazz.__setattr__ = new_setattr

    instance.__attr_change_monitor_on_change = on_change


import pytest
from dataclasses import dataclass
from typing import List


@dataclass
class TestClass:
    value: int = 0
    name: str = ""


def test_monitor_existing_property_change():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        changes.append(change)

    obj = TestClass(value=10)
    monitor_property_changes(obj, on_change)

    obj.value = 20

    assert len(changes) == 1
    assert changes[0] == PropertyChange("value", 10, 20)


def test_monitor_new_property_addition():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        changes.append(change)

    obj = TestClass()
    monitor_property_changes(obj, on_change)

    obj.new_prop = "new"

    assert len(changes) == 0  # New property additions are not monitored


def test_monitor_multiple_changes():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        changes.append(change)

    obj = TestClass(value=5, name="test")
    monitor_property_changes(obj, on_change)

    obj.value = 10
    obj.name = "updated"
    obj.value = 15

    assert len(changes) == 3
    assert changes[0] == PropertyChange("value", 5, 10)
    assert changes[1] == PropertyChange("name", "test", "updated")
    assert changes[2] == PropertyChange("value", 10, 15)


def test_monitor_unchanged_value():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        changes.append(change)

    obj = TestClass(value=5)
    monitor_property_changes(obj, on_change)

    obj.value = 5  # Setting to the same value

    assert len(changes) == 1  # The change is still recorded even if the value is the same


def test_monitor_multiple_instances():
    changes1: List[PropertyChange] = []
    changes2: List[PropertyChange] = []

    def on_change1(change: PropertyChange):
        changes1.append(change)

    def on_change2(change: PropertyChange):
        changes2.append(change)

    obj1 = TestClass(value=1)
    obj2 = TestClass(value=2)

    monitor_property_changes(obj1, on_change1)
    monitor_property_changes(obj2, on_change2)

    obj1.value = 10
    obj2.value = 20

    assert len(changes1) == 1
    assert changes1[0] == PropertyChange("value", 1, 10)
    assert len(changes2) == 1
    assert changes2[0] == PropertyChange("value", 2, 20)
