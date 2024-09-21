from dataclasses import dataclass
from wwwpy.common import property_monitor as pm


@dataclass
class TestClass:
    value: int = 0
    name: str = ""

    def __setattr__(self, key, value):
        # if hasattr(self, key):
        #     print(f"Change detected: {key} from {getattr(self, key)} to {value}")
        super().__setattr__(key, value)


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
