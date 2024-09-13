import sys
from pathlib import Path

from tests.common import restore_sys_path
from wwwpy.common.designer.html_locator import Node
from wwwpy.common.designer.code_path import TargetLocation


def test_resolve(tmp_path, restore_sys_path):
    # GIVEN
    # it looks like the 'remote' is already importable because the 'remote' from '/tests' is imported
    package1 = tmp_path / 'package1'
    package1.mkdir()
    (package1 / '__init__.py').write_text('')
    component2_py = package1 / 'component2.py'
    component2_py.write_text('''

class Component2: ...
    ''')
    sys.path.insert(0, str(tmp_path))

    from package1.component2 import Component2
    component2 = Component2()

    path = [Node("DIV", 1, {'class': 'class1'})]
    target = TargetLocation(component2, path)

    # WHEN
    res = target.resolve()

    # THEN
    assert res.path is path
    assert res.class_name == 'Component2'
    assert res.class_module == 'package1.component2'
    assert Path(res.relative_path) == Path('package1/component2.py')  # issue with windows path
    assert res.concrete_path == str(component2_py)
