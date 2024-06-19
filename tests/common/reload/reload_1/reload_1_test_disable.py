from pathlib import Path


def test_1():
    import component

    assert component.Class1().a == 123

    # beware of issue https://stackoverflow.com/questions/71544388/understanding-pythons-importlib-reload
    component_file = (Path(__file__).parent / 'component.py')
    component_file.write_text(component_file.read_text().replace('.a = 123', '.b = 45'))

    from wwwpy.common import reloader
    reloader.reload(component)

    assert component.Class1().b == 45
