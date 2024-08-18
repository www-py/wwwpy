from pathlib import Path

from wwwpy.common.filesystem.sync import Event


def event_apply(path: Path, event: Event) -> Path:
    src_full_path = path / event.src_path
    dest_full_path = path / event.dest_path if event.dest_path else None

    if event.event_type == 'created':
        if event.is_directory:
            src_full_path.mkdir(exist_ok=True)
        else:
            src_full_path.touch()

    elif event.event_type == 'deleted':
        if event.is_directory:
            src_full_path.rmdir()
        else:
            src_full_path.unlink()

    elif event.event_type == 'modified':
        if not event.is_directory:
            # For simplicity, we'll just update the file's content
            # In a real scenario, you might want to store the old content somewhere
            src_full_path.write_text(f"Modified content at {src_full_path}")

    elif event.event_type == 'moved':
        src_full_path.rename(dest_full_path)

    # For 'closed' event, we don't need to do anything

    return path