from dataclasses import dataclass
from typing import List

from wwwpy.common import property_monitor as pm
from wwwpy.common.property_monitor import PropertyChange, monitor_property_changes


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


def test_monitor_on_second_instance():
    changes: List[PropertyChange] = []

    def on_change(change: PropertyChange):
        pass

    def on_change2(change: PropertyChange):
        changes.append(change)

    obj1 = TestClass(value=10)
    monitor_property_changes(obj1, on_change)
    obj = TestClass(value=10)
    monitor_property_changes(obj, on_change2)

    obj.value = 20

    assert len(changes) == 1
    assert changes[0] == PropertyChange("value", 10, 20)


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
