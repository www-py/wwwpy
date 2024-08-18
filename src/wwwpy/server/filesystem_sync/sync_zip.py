from __future__ import annotations

import base64
import os
import zipfile
from io import BytesIO
from pathlib import Path

import shutil
from pathlib import Path
from typing import List, Any

from wwwpy.common.filesystem.sync import Event


def sync_source(source: Path, events: List[Event]) -> List[Any]:
    if not events:
        return []
    return sync_init(source)


def _delete_recursive(path: Path, ignore_errors):
    for e in path.iterdir():
        if e.is_file():
            e.unlink(missing_ok=ignore_errors)
        elif e.is_dir():
            shutil.rmtree(e, ignore_errors=ignore_errors)


def sync_target(target_root: Path, changes: List[Any]) -> None:
    if not changes:
        return
    _delete_recursive(target_root, ignore_errors=True)
    _delete_recursive(target_root, ignore_errors=False)

    b = base64.b64decode(changes[0])
    with BytesIO(b) as stream:
        with zipfile.ZipFile(stream, "r") as zip_file:
            zip_file.extractall(target_root)


def sync_init(source: Path) -> List[Any]:
    b = _zip_in_memory(source)
    s = base64.b64encode(b).decode('utf-8')
    return [s]


def _zip_path(zip_file, path):
    if os.path.isfile(path):
        zip_file.write(path, os.path.basename(path))
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, path)
                zip_file.write(file_path, arcname)


def _zip_in_memory(path) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zip_file:
        _zip_path(zip_file, path)

    stream.seek(0)
    return stream.getbuffer().tobytes()
