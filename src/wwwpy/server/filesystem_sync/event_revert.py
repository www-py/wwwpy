from pathlib import Path
from typing import Dict, Any
import shutil

from wwwpy.common.filesystem.sync import Event


def event_revert(path: Path, event: Event, file_contents: Dict[str, str]) -> Path:
    src_full_path = path / event.src_path
    dest_full_path = path / event.dest_path if event.dest_path else None

    if event.event_type == 'created':
        if event.is_directory:
            shutil.rmtree(src_full_path)
        else:
            src_full_path.unlink()

    elif event.event_type == 'deleted':
        if event.is_directory:
            src_full_path.mkdir(parents=True, exist_ok=True)
        else:
            src_full_path.touch()
            if event.src_path in file_contents:
                src_full_path.write_text(file_contents[event.src_path])

    elif event.event_type == 'modified':
        if not event.is_directory:
            if event.src_path in file_contents:
                src_full_path.write_text(file_contents[event.src_path])
            else:
                # If we don't have the previous content, we can't revert properly
                # For now, we'll just empty the file
                src_full_path.write_text('')

    elif event.event_type == 'moved':
        if dest_full_path.exists():
            if event.is_directory:
                shutil.move(str(dest_full_path), str(src_full_path))
            else:
                dest_full_path.rename(src_full_path)

    # For 'closed' event, we don't need to do anything

    return path