import tempfile
from pathlib import Path
from typing import List, Protocol, Any

from wwwpy.common.filesystem.sync.event import Event


def new_tmp_path() -> Path:
    return Path(tempfile.mkdtemp(prefix='debounce-tmp-path-'))


def filesystemevents_print(events: List[Event], package:str=''):
    # for e in events:
    #     print(f'  {e}')
    def accept(e: Event) -> bool:
        bad = e.is_directory and e.event_type == 'modified'
        return not bad
    def to_str(e: Event) -> str:
        return e.src_path if e.dest_path == '' else f'{e.src_path} -> {e.dest_path}'
    joined = set(to_str(e) for e in events if accept(e))
    summary = ', '.join(joined)
    if package != '':
        package = f' for `{package}`'
    print(f'Hotreload event{package} count: {len(events)}. Changes summary: {summary}')


class Sync(Protocol):

    @staticmethod
    def sync_source(source: Path, events: List[Event]) -> List[Any]:
        """Could be called 'sync_produce'. This part has the following input:
- a reference to the root of the monitored source filesystem
- a list of filesystem change events


The output is:
- a list of filesystem changes that can be serialized.
- such list can be an aggregated list of changes (e.g., a file was created and then modified, the two events can be aggregated into a single event)

"""

    @staticmethod
    def sync_target(target: Path, changes: List[Any]) -> None:
        """Could be called 'sync_apply'. This part has the following input:
- a reference to the root of the target filesystem
- a list of filesystem aggregated change events

The output is:
- the target filesystem is updated to reflect the changes
"""

    @staticmethod
    def sync_init(source: Path) -> List[Any]:
        """This part has the following input:
- a reference to the root of the monitored source filesystem

The output is:
- a list of filesystem aggregated change events that reflect the current state of the source filesystem
"""
