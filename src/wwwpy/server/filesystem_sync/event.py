import dataclasses
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Event:
    event_type: str
    is_directory: bool
    src_path: str
    dest_path: str = ''

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
        src_path = '' if e.src_path == '' else str(into / e.src_path)
        dest_path = '' if e.dest_path == '' else str(into / e.dest_path)
        return dataclasses.replace(e, src_path=src_path, dest_path=dest_path)
