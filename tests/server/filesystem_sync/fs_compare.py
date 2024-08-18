import filecmp
from pathlib import Path


class FsCompare:

    def __init__(self, left: Path, right: Path, left_name: str, right_name: str):
        self.left = left
        self.right = right
        self.left_name = left_name
        self.right_name = right_name
        self.dircmp = None

    def synchronized(self):
        self._dircmp()
        return self._is_synchronized()

    def _is_synchronized(self) -> bool:
        return not self.dircmp.left_only and not self.dircmp.right_only and not self.dircmp.diff_files

    def sync_error(self):
        self._dircmp()

        def diff_printable():
            return (f'{self.left_name}-only={self.dircmp.left_only} {self.right_name}-only={self.dircmp.right_only}'
                    f' diff-files={self.dircmp.diff_files}')

        return None if self._is_synchronized() else diff_printable()

    def _dircmp(self):
        if not self.dircmp:
            self.dircmp = filecmp.dircmp(self.left, self.right)
