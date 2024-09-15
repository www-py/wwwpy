from pathlib import Path

from tests.common import dyn_sys_path
from wwwpy.common.designer.element_path import ElementPath
from wwwpy.common.designer.html_locator import Node


def test_calculated_attributes(dyn_sys_path):
    # GIVEN
    component2_py = dyn_sys_path.write_module('package1', 'component2.py', '''

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
