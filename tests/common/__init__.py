import sys

import pytest


@pytest.fixture
def restore_sys_path():
    sys_path = sys.path.copy()
    sys_meta_path = sys.meta_path.copy()
    yield
    sys.path = sys_path
    sys.meta_path = sys_meta_path
