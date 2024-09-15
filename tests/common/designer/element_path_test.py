from pathlib import Path

from tests.common import path_unloader
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node


def test_calculated_attributes(path_unloader):
    # GIVEN
    # it looks like the 'remote' is already importable because the 'remote' from '/tests' is imported
    tmp_path = path_unloader.tmp_path
    package1 = tmp_path / 'package1'
    package1.mkdir()
    (package1 / '__init__.py').write_text('')
    component2_py = package1 / 'component2.py'
    component2_py.write_text('''

class Component2: ...
    ''')

    from package1.component2 import Component2
    component2 = Component2()

    path = [Node("div", 1, {'class': 'class1'})]

    # WHEN
    target = ElementPath(component2, path)

    # THEN
    assert target.path is path
    assert target.class_name == 'Component2'
    assert target.class_module == 'package1.component2'
    assert Path(target.relative_path) == Path('package1/component2.py')  # issue with windows path
    assert target.concrete_path == str(component2_py)
