from dataclasses import dataclass
from typing import Callable, List


@dataclass
class PropertyChange:
    instance: any
    name: str
    old_value: object
    new_value: object


def monitor_property_changes(instance, on_change: Callable[[List[PropertyChange]], None]):
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
                self.__attr_change_monitor_on_change([change])
            original_setattr(self, name, value)

        clazz.__setattr__ = new_setattr

    instance.__attr_change_monitor_on_change = on_change


from contextlib import contextmanager


@contextmanager
def group_changes(instance):
    old = instance.__attr_change_monitor_on_change
    buffer = []

    def _in_buffer(changes):
        buffer.extend(changes)

    instance.__attr_change_monitor_on_change = _in_buffer
    try:
        yield instance
    finally:
        instance.__attr_change_monitor_on_change = old
        if buffer:
            old(buffer)
