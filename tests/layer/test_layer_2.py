import os
from pathlib import Path
from typing import Optional, NamedTuple
from io import BytesIO
from zipfile import ZipFile

from wwwpy.resources import from_filesystem, PathResource, Resource, default_resource_filter, build_archive, \
    StringResource, stacktrace_pathfinder, _is_path_contained

parent = Path(__file__).parent


class Test_ResourceIterator_from_filesystem:
    support_data = parent / 'support_data/from_filesystem'

    def test_one_file(self):
        folder = self.support_data / 'one_file'
        actual = set(from_filesystem(folder))
        expect = {PathResource('foo.py', folder / 'foo.py')}
        assert expect == actual

    def test_zero_file(self):
        folder = self.support_data / 'zero_file'
        folder.mkdir(exist_ok=True)  # git does not commit empty folders
        actual = set(from_filesystem(folder))
        expect = set()
        assert expect == actual

    def test_selective(self):
        folder = self.support_data / 'relative_to'
        actual = set(from_filesystem(folder / 'yes', relative_to=folder))
        expect = {PathResource(fix_sep('yes/yes.txt'), folder / 'yes/yes.txt')}
        assert expect == actual

    def test_resource_filter(self):
        folder = self.support_data / 'item_filter'
        reject = folder / 'yes/reject'

        pycache = folder / 'yes/__pycache__'
        pycache.mkdir(exist_ok=True)
        (pycache / 'cache.txt').write_text('some cache')

        def resource_filter(item: Resource) -> Optional[Resource]:
            if item.filepath == reject:
                return None
            return default_resource_filter(item)

        actual = set(from_filesystem(folder, resource_filter=resource_filter))
        expect = {PathResource(fix_sep('yes/yes.txt'), folder / 'yes/yes.txt')}
        assert expect == actual


class Test_build_archive:
    support_data = parent / 'support_data/build_archive'

    def test_build_archive(self):
        class ZFile(NamedTuple):
            filename: str
            content: bytes

        folder = self.support_data / 'simple'
        (folder / 'empty_dir').mkdir(exist_ok=True)  # should be ignored by build_archive

        archive_bytes = build_archive(list(from_filesystem(folder)) +
                                      [StringResource('dir1/baz.txt', "#baz")])

        actual_files = set()
        with ZipFile(BytesIO(archive_bytes)) as zf:
            for il in zf.infolist():
                with zf.open(il, 'r') as file:
                    actual_files.add(ZFile(il.filename, file.read()))

        expected_files = {
            ZFile('foo.txt', '#foo'.encode()),
            ZFile('dir1/bar.txt', '#bar'.encode()),
            ZFile('dir1/baz.txt', '#baz'.encode()),
        }

        assert expected_files == actual_files


class Test_stacktrace_pathfinder:

    def test_external_filename(self):
        actual = stacktrace_pathfinder()
        assert actual == Path(__file__).resolve()

    def test_is_contained_into(self):
        assert _is_path_contained(Path('/foo/bar'), Path('/foo/bar/baz')) is False

    def test_is_contained_into_2(self):
        assert _is_path_contained(Path('/foo/xxx'), Path('/foo/bar/baz')) is False

    def test_is_contained_into_3(self):
        assert _is_path_contained(Path('/foo/bar/baz/yyy'), Path('/foo/bar/baz')) is True

    def test_is_contained_into_4(self):
        assert _is_path_contained(Path('/foo/bar/baz'), Path('/foo/bar/baz')) is True


def fix_sep(path: str) -> str:
    return path.replace('/', os.path.sep)
