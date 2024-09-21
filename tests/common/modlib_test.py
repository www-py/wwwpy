import sys

from tests.common import restore_sys_path
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
