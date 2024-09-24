from pathlib import Path

from tests.common import restore_sys_path
from wwwpy.common.modlib import _find_module_path
from wwwpy.server import configure


def test_dev_mode_disabled__should_NOT_create_canonical_components(restore_sys_path, tmp_path: Path):
    configure.convention(tmp_path)
    assert get_all_paths_with_hashes(tmp_path) == set()


def test_dev_mode_empty_folder__should_create_canonical_components(restore_sys_path, tmp_path: Path):
    configure.convention(tmp_path, dev_mode=True)

    dir1 = _find_module_path('wwwpy.common').parent / 'quickstart/setup1'
    dir2 = tmp_path
    dir1_set = get_all_paths_with_hashes(dir1)
    dir2_set = get_all_paths_with_hashes(dir2)
    assert dir1_set == dir2_set, "Directories do not match!"


def test_dev_mode_non_empty_folder_but_no_remote__should_not_fail(restore_sys_path, tmp_path: Path):
    # tmp_path.mkdir('some-folder')
    (tmp_path / 'some-folder').mkdir()
    configure.convention(tmp_path, dev_mode=True)


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
