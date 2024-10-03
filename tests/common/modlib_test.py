import sys

from tests.common import restore_sys_path, dyn_sys_path, DynSysPath
from wwwpy.common.modlib import _find_module_path


def test_package_path(tmp_path, restore_sys_path):
    # GIVEN
    sys.path.insert(0, str(tmp_path))
    mod1py = tmp_path / 'module1.py'
    mod1py.write_text(' invalid  python ')

    # WHEN
    target = _find_module_path('module1')
    # THEN
    assert target is not None
    assert str(mod1py) == str(target)


def test_package_path2(dyn_sys_path: DynSysPath):
    # GIVEN
    mod1py = dyn_sys_path.write_module('package1', 'module1', ' I am module1')
    dyn_sys_path.write_module('package1', '__init__', 'I am package1')

    # WHEN
    target = _find_module_path('package1.module1')
    # THEN
    assert target is not None
    assert str(mod1py) == str(target)


def test_package_path3(dyn_sys_path: DynSysPath):
    # GIVEN
    dyn_sys_path.write_module('p1', 'p2', 'import xyz')
    mod1py= dyn_sys_path.write_module('p1.p2', 'm1', 'import xyz')

    # WHEN
    target = _find_module_path('p1.p2.m1')
    # THEN
    assert target is not None
    assert str(mod1py) == str(target)

def test_package_path4(dyn_sys_path: DynSysPath):
    # GIVEN

    # WHEN
    target = _find_module_path('wwwpy.remote.component')
    # THEN
    assert target is not None
    assert target.name == 'component.py'

def test_package_not_found():
    # GIVEN

    # WHEN
    target = _find_module_path('package_not_exists')
    # THEN
    assert target is None