import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Optional

from wwwpy.common.rpc import serialization
from wwwpy.common.filesystem.sync import Event


@dataclass
class Operation:
    op_type: str
    is_dir: bool
    path: str
    was: str = ""
    content_bytes: Optional[bytes] = None
    content_str: Optional[str] = None


def sync_source(source: Path, events: List[Event]) -> List[Any]:
    res = _make_summary(source, events)
    ser = serialization.serialize(res, List[Operation])
    return ser


def _make_summary(source: Path, events: List[Event]) -> List[Operation]:
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
            result.append(Operation(op_type='delete', is_dir=False, path=str(name)))
        elif status == 'modified':
            _append_file(result, name, path)
    return result


def _append_file(result, name, path):
    if path.is_file() and path.exists():
        try:
            result.append(Operation(op_type='write', is_dir=False, path=str(name), content_str=path.read_text()))
            # result.append({'name': str(name), 'content': path.read_text()})
        except UnicodeDecodeError:
            result.append(Operation(op_type='write', is_dir=False, path=str(name), content_bytes=path.read_bytes()))
        except Exception as e:
            pass


def sync_target(target_root: Path, changes: List[Any]) -> None:
    res = serialization.deserialize(changes, List[Operation])
    _apply_summary(target_root, res)


def _apply_summary(target_root: Path, changes: List[Operation]) -> None:
    for change in changes:
        target = target_root / change.path
        if change.op_type == 'delete':
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
        elif change.op_type == 'write':

            content = change.content_str
            if content is None:
                content = change.content_bytes

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
    summary = _make_initial_summary(source)
    serialize = serialization.serialize(summary, List[Operation])
    return serialize


def _make_initial_summary(source: Path) -> List[Operation]:
    result = []
    for path in source.rglob('*'):
        _append_file(result, path.relative_to(source), path)
    return result
