import base64
import mimetypes

from js import console, document
from pathlib import Path


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

