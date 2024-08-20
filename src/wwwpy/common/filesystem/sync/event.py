from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from optparse import Option
from pathlib import Path
from typing import AnyStr, Union, Optional


@dataclass(frozen=True)
class Event:
    event_type: str
    is_directory: bool
    src_path: str
    dest_path: str = ''
    content: Union[str, bytes, None] = None

    def strip_container(self, container_path: str) -> 'Event':
        if (not self.src_path.startswith(container_path) or (
                self.dest_path and not self.dest_path.startswith(container_path))):
            raise ValueError(f'Paths are not contained in {container_path} self={self}')

        len_cont = len(container_path)

        def fix(path: str) -> str:
            if path == '':
                return ''
            new_path = path[len_cont:]
            if new_path == '':
                return '/'
            return new_path

        src_path = fix(self.src_path)
        dest_path = fix(self.dest_path)

        return Event(self.event_type, self.is_directory, src_path, dest_path)

    def to_absolute(self, into: Path) -> 'Event':
        e = self
        src_path = (into / e.src_path).as_posix()
        dest_path = '' if e.dest_path == '' else (into / e.dest_path).as_posix()
        return dataclasses.replace(e, src_path=src_path, dest_path=dest_path)

    def relative_to(self, other):
        e = self
        if e.src_path == '' or e.src_path == '/':
            raise ValueError(f'Invalid src_path: {e.src_path}')
        src = Path(e.src_path).relative_to(other)
        res = dataclasses.replace(e, src_path=src.as_posix())

        if e.dest_path == '':
            return res
        if e.dest_path and (e.dest_path == '' or e.dest_path == '/'):
            raise ValueError(f'Invalid dest_path: {e.dest_path}')
        dst = Path(e.dest_path).relative_to(other)
        res2 = dataclasses.replace(res, dest_path=dst.as_posix())
        return res2
