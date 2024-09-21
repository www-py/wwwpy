from dataclasses import dataclass
from typing import Callable


@dataclass
class PropertyChange:
    name: str
    old_value: object
    new_value: object


def monitor_property_changes(instance, on_change: Callable[[PropertyChange], None]):
    """Monitor the changes of the properties of an instance of a class.
    When a property is changed, the on_change callback is called with the name of the property, the old value and the new value.

    :param instance: The instance of the class to monitor
    :param on_change: The callback to call when a property is changed
    """
    if not hasattr(instance, "__attr_change_monitor"):
        setattr(instance, "__attr_change_monitor", True)

        original_setattr = instance.__class__.__setattr__  # Keep a reference to the original method

        def new_setattr(self, name, value):
            if hasattr(self, name):
                change = PropertyChange(name, getattr(self, name), value)
                on_change(change)
            original_setattr(self, name, value)

        instance.__class__.__setattr__ = new_setattr.__get__(instance, instance.__class__)


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
