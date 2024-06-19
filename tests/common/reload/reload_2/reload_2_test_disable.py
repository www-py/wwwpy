from pathlib import Path

parent = Path(__file__).parent / 'package2'


def test_2():
    replace((parent / 'class_a.py'), '.b = 45', '.a = 123')
    replace((parent / 'class_b.py'), '.b = 45', '.a = 123')

    import package2.class_a

    assert package2.class_a.ClassA().a == 123
    assert package2.class_a.ClassA().class_b.a == 123

    # beware of issue https://stackoverflow.com/questions/71544388/understanding-pythons-importlib-reload
    replace((parent / 'class_a.py'), '.a = 123', '.b = 45')
    replace((parent / 'class_b.py'), '.a = 123', '.b = 45')

    # from wwwpy.common import reloader
    # reloader.reload(package2)
    # reloader.reload(package2.class_a)
    # reloader.reload(package2.class_b)
    import importlib
    # del package2.class_a.class_b
    # importlib.invalidate_caches()
    importlib.reload(package2.class_a)
    importlib.reload(package2.class_a.class_b)

    assert package2.class_a.ClassA().b == 45
    assert package2.class_a.ClassA().class_b.b == 45


def replace(path, old, new):
    path.write_text(path.read_text().replace(old, new))


from types import ModuleType
import sys
import importlib


def deep_reload(m: ModuleType):
    name = m.__name__  # get the name that is used in sys.modules
    name_ext = name + '.'  # support finding sub modules or packages

    def compare(loaded: str):
        return (loaded == name) or loaded.startswith(name_ext)

    all_mods = tuple(sys.modules)  # prevent changing iterable while iterating over it
    sub_mods = filter(compare, all_mods)
    for pkg in sorted(sub_mods, key=lambda item: item.count('.'), reverse=True):
        importlib.reload(sys.modules[pkg])  # reload packages, beginning with the most deeply nested
