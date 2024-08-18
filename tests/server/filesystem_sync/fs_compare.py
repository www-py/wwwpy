import filecmp
from pathlib import Path


class FsCompare:

    def __init__(self, left: Path, right: Path, left_name: str, right_name: str):
        self.left = left
        self.right = right
        self.left_name = left_name
        self.right_name = right_name
        self.dircmp = None
        self.type_mismatches = []

    def synchronized(self):
        self._dircmp()
        return self._is_synchronized()

    def _is_synchronized(self) -> bool:
        return (not self.dircmp.left_only and
                not self.dircmp.right_only and
                not self.dircmp.diff_files and
                not self.type_mismatches)

    def sync_error(self):
        self._dircmp()

        def diff_printable():
            return (f'{self.left_name}-only={self.dircmp.left_only} '
                    f'{self.right_name}-only={self.dircmp.right_only} '
                    f'diff-files={self.dircmp.diff_files} '
                    f'type-mismatches={self.type_mismatches}')

        return None if self._is_synchronized() else diff_printable()

    def _dircmp(self):
        if not self.dircmp:
            self.dircmp = filecmp.dircmp(self.left, self.right)
            self._check_type_mismatches()

    def _check_type_mismatches(self):
        self.type_mismatches = []
        all_names = set(self.dircmp.left_list + self.dircmp.right_list)

        for name in all_names:
            left_path = self.left / name
            right_path = self.right / name

            if left_path.exists() and right_path.exists():
                if left_path.is_file() != right_path.is_file():
                    self.type_mismatches.append(name)

        # Remove type mismatches from other lists to avoid duplication
        self.dircmp.left_only = [item for item in self.dircmp.left_only if item not in self.type_mismatches]
        self.dircmp.right_only = [item for item in self.dircmp.right_only if item not in self.type_mismatches]
        self.dircmp.diff_files = [item for item in self.dircmp.diff_files if item not in self.type_mismatches]