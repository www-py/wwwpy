import base64
import shutil
from pathlib import Path
from typing import List, Any

from watchdog.events import FileSystemEvent


def sync_source(source: Path, events: List[FileSystemEvent]) -> List[Any]:
    state = {}
    moved = {}
    for e in events:
        src = Path(e.src_path)
        name = str(src.relative_to(source))
        prev = state.get(name, None)
        if e.is_directory:
            if e.event_type == 'deleted':
                for name_p in list(state.keys()):
                    if name_p.startswith(name):
                        del state[name_p]
                state[name] = 'deleted'

        else:  # is file
            if e.event_type == 'moved':
                dst = Path(e.dest_path)
                dst_name = str(dst.relative_to(source))
                moved[dst_name] = name
            if e.event_type == 'created':
                state[name] = 'modified'
            if e.event_type == 'modified':
                state[name] = state.get(name, 'modified')  # if it was created, it stays created
            elif e.event_type == 'deleted':
                if prev == 'modified':
                    del state[name]
                else:
                    state[name] = 'deleted'

    result = []
    for name, status in state.items():
        path = source / name
        if status == 'deleted':
            result.append({'name': str(name), 'content': None})
        elif status == 'modified':
            _append_file(result, name, path)
    return result


def _append_file(result, name, path):
    if path.is_file() and path.exists():
        try:
            result.append({'name': str(name), 'content': path.read_text()})
        except UnicodeDecodeError:
            b64 = base64.b64encode(path.read_bytes()).decode('utf-8')
            result.append({'name': str(name), 'content_b64': b64})
        except Exception as e:
            pass
            # import traceback
            # msg = f'Error reading {path}: {e}\n{traceback.format_exc()}'
            # print(msg)


def sync_target(target_root: Path, changes: List[Any]) -> None:
    for change in changes:
        target = target_root / change['name']
        content = change.get('content', None)
        if content is None and 'content_b64' in change:
            content = base64.b64decode(change['content_b64'])
        if content is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content)
        else:
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)


def sync_init(source: Path) -> List[Any]:
    result = []
    for path in source.rglob('*'):
        _append_file(result, path.relative_to(source), path)
    return result
