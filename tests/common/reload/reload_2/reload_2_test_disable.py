from pathlib import Path


def test_2():
    from package2 import class_a

    assert class_a.ClassA().a == 123
    assert class_a.ClassA().class_b.a == 123

    # beware of issue https://stackoverflow.com/questions/71544388/understanding-pythons-importlib-reload
    parent = Path(__file__).parent / 'package2'
    replace((parent / 'class_a.py'), '.a = 123', '.b = 45')
    replace((parent / 'class_b.py'), '.a = 123', '.b = 45')

    from wwwpy.common import reloader
    import package2
    reloader.reload(package2)

    assert class_a.ClassA().b == 45
    assert class_a.ClassA().class_b.b == 5


def replace(path, old, new):
    path.write_text(path.read_text().replace(old, new))
