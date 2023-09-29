# Browse pyscript virtual filesystem
from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from js import console
from pyodide.ffi import create_proxy, create_once_callable

# from wwwpy.remote.asyncjs import set_timeout
from wwwpy.common.files import download_bytes, zip_in_memory

HTMLElement = TypeVar('HTMLElement')
from wwwpy.remote.widget import Widget


class FilesystemTreeWidget(Widget):
    def __init__(self, path: Path = Path('/'), indent=1):
        self._indent = indent
        super().__init__(  # language=HTML
            f"""
            <span id="_entity"></span>
            <span id="_download">&nbsp ↓ &nbsp</span>
            <div id="_children" style="margin-left: 1em"></div>
            
            """
        )
        self.path = Path(path)
        self._entity: HTMLElement = self
        self._children: HTMLElement = self
        self._download: HTMLElement = self

    def after_render(self):
        from js import window
        window.setTimeout(create_once_callable(self._after_append), 10)

    async def _after_append(self):
        self._entity.onclick = create_proxy(self.toggle_display)
        self._download.onclick = create_proxy(self.download)

        # if not self.is_dir():
        #     self._download.style.display = 'none'

        if self._indent > 1:
            self.toggle_display()

        self._update_caption()

        if self.is_dir():
            self._recurse()

    def is_dir(self):
        # return self.path.is_dir() # in pyodide: `PermissionError: [Errno 63] Operation not permitted: '/proc/self/fd'`
        return os.path.isdir(self.path)

    def toggle_display(self, *args):
        self._children.style.display = '' if self._children_hidden() else 'none'
        self._update_caption()

    def download(self, *args):
        console.log(f'click {self.path.absolute()}')
        if self.is_dir():
            download_bytes(self.path.name + '.zip', zip_in_memory(self.path))
        else:
            download_bytes(self.path.name, self.path.read_bytes())

    def _update_caption(self):
        if_dir = '▸' if self._children_hidden() else '▼'
        pre = if_dir if self.is_dir() else ' '
        self._entity.innerHTML = (f'<span style="display:inline-block; width: 1em">{pre}</span>'
                                  + ' ' + self.path.name)

    def _children_hidden(self):
        s = self._children.style
        return not s.display == ''

    def _recurse(self):
        for child in self.path.glob('*'):
            w = FilesystemTreeWidget(child, self._indent + 1)
            w.append_to(self._children)
