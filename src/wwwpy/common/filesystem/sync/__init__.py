import tempfile
from pathlib import Path
from typing import List, Protocol, Any

from wwwpy.common.filesystem.sync.event import Event


def new_tmp_path() -> Path:
    return Path(tempfile.mkdtemp(prefix='debounce-tmp-path-'))

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
