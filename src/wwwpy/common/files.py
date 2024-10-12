from __future__ import annotations

import hashlib
import os
import zipfile
from io import BytesIO
from pathlib import Path

directory_blacklist = {'.mypy_cache', '__pycache__', '.DS_Store'}
_bundle_path = '/wwwpy_bundle'


def _zip_path(zip_file, path):
    path = str(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_file.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '../remote')))


def zip_in_memory(path):
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zip_file:
        _zip_path(zip_file, path)

    stream.seek(0)
    return stream.getbuffer().tobytes()


def get_all_paths_with_hashes(path: str | Path) -> set[tuple[str, str | None]]:
    path = Path(path)
    paths = set()
    for path in path.rglob('*'):
        relative_path = path.relative_to(path)
        if path.is_file():
            file_hash = get_file_hash(path)
            paths.add((str(relative_path), file_hash))
        else:
            paths.add((str(relative_path), None))  # Directories don't need a hash
    return paths


def get_file_hash(filepath: str | Path) -> str:
    hash_sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
