from __future__ import annotations

import base64
import mimetypes
import os
import zipfile
from io import BytesIO
from pathlib import Path

directory_blacklist = {'.mypy_cache', '__pycache__'}


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
