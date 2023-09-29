from __future__ import annotations

import base64
import mimetypes
import os
import zipfile
from io import BytesIO
from pathlib import Path

from js import console, document


def download_path(filename: str, path: Path, mime_type: str = None):
    download_bytes(filename, path.read_bytes(), mime_type)


def download_bytes(filename: str, content: bytes, mime_type: str = None):
    if mime_type is None:
        gt = mimetypes.guess_type(filename)
        mime_type = gt[0]
        if mime_type is None:
            mime_type = 'application/octet-stream'
        console.log(f'guess mime type for `{filename}` is `{mime_type}`')
    a = document.createElement('a')
    a.download = filename
    a.href = f'data:{mime_type};base64,{base64.b64encode(content).decode("ascii")}'
    document.body.append(a)
    a.click()


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
