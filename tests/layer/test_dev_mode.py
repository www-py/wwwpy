from tests.common import dyn_sys_path, DynSysPath
from wwwpy.common import modlib
from wwwpy.server import configure


def test_dev_mode_disabled__should_NOT_create_canonical_components(dyn_sys_path: DynSysPath):
    configure.convention(dyn_sys_path.path)
    assert get_all_paths_with_hashes(dyn_sys_path.path) == set()


def test_dev_mode_non_empty_folder_but_no_remote__should_not_fail(dyn_sys_path: DynSysPath):
    # dyn_sys_path.path.mkdir('some-folder')
    (dyn_sys_path.path / 'some-folder').mkdir()
    configure.convention(dyn_sys_path.path, dev_mode=True)


from pathlib import Path
import hashlib


def get_all_paths_with_hashes(root):
    root = Path(root)
    paths = set()
    for path in root.rglob('*'):
        relative_path = path.relative_to(root)
        if path.is_file():
            file_hash = get_file_hash(path)
            paths.add((str(relative_path), file_hash))
        else:
            paths.add((str(relative_path), None))  # Directories don't need a hash
    return paths


def get_file_hash(filepath):
    hash_sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
