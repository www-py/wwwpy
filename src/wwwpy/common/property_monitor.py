from dataclasses import dataclass
from typing import Callable, List
from contextlib import contextmanager


@dataclass
class PropertyChanged:
    instance: any
    name: str
    old_value: object
    new_value: object


def monitor_changes(instance, on_changed: Callable[[List[PropertyChanged]], None]):
    """Monitor the changes of the properties of an instance of a class."""
    if hasattr(instance, "__attr_change_monitor_on_changed"):
        raise Exception("The instance is already being monitored for property changes")

    clazz = instance.__class__
    if not hasattr(clazz, "__attr_change_monitor"):
        setattr(clazz, "__attr_change_monitor", True)

        original_setattr = clazz.__setattr__  # Keep a reference to the original method

        def new_setattr(self, name, value):
            doit = (hasattr(self, name) and name != "__attr_change_monitor_on_changed" and
                    hasattr(self, "__attr_change_monitor_on_changed"))
            if doit:
                change = PropertyChanged(self, name, getattr(self, name), value)
            original_setattr(self, name, value)
            if doit:
                self.__attr_change_monitor_on_changed([change])

        clazz.__setattr__ = new_setattr

    instance.__attr_change_monitor_on_changed = on_changed


@contextmanager
def group_changes(instance):
    old = instance.__attr_change_monitor_on_changed
    buffer = []

    def _in_buffer(changes):
        buffer.extend(changes)

    instance.__attr_change_monitor_on_changed = _in_buffer
    try:
        yield instance
    finally:
        instance.__attr_change_monitor_on_changed = old
        if buffer:
            old(buffer)
