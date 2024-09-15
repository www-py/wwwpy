import sys
from pathlib import Path

import pytest


@pytest.fixture
def restore_sys_path():
    sys_path = sys.path.copy()
    sys_meta_path = sys.meta_path.copy()
    try:
        yield
    finally:
        sys.path = sys_path
        sys.meta_path = sys_meta_path


class PathUnloader:
    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path


@pytest.fixture
def path_unloader(tmp_path: Path):
    sys.path.insert(0, str(tmp_path))
    pu = PathUnloader(tmp_path)
    try:
        yield pu
    finally:
        sys.path.remove(str(tmp_path))
        import wwwpy.common.reloader as r
        r.unload_path(str(tmp_path))
