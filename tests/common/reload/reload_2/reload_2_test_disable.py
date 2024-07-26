from pathlib import Path

from wwwpy.common.implib import _find_module_path
from wwwpy.common.reloader import unload_path

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

    p2 = _find_module_path('package2')

    unload_path(str(p2.parent))

    del package2.class_a
    import package2.class_a
    assert package2.class_a.ClassA().b == 45
    assert package2.class_a.ClassA().class_b.b == 45


def replace(path, old, new):
    path.write_text(path.read_text().replace(old, new))
