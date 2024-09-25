from __future__ import annotations

import sys
from typing import List, Any

from wwwpy.common import modlib
from wwwpy.remote import rpc as rpc
from js import console

_wwwpy_dev_mode = 'wwwpy_dev_mode'


async def activate():
    setattr(sys, _wwwpy_dev_mode, True)
    from wwwpy.remote import micropip_install
    from wwwpy.common import designer

    from wwwpy.common.filesystem.sync import sync_delta2
    from wwwpy.common.filesystem.sync import Sync
    sync_impl: Sync = sync_delta2

    for package in designer.pypi_packages:
        await micropip_install(package)

    def file_changed(package_name: str, events: List[Any]):
        directory = modlib._find_package_directory(package_name)
        sync_impl.sync_target(directory, events)

        from wwwpy.remote.browser_main import _reload
        _reload()

    rpc.file_changed_listeners_add(file_changed)


def is_active() -> bool:
    return hasattr(sys, _wwwpy_dev_mode)
