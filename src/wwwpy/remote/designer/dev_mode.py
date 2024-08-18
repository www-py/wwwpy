from __future__ import annotations

from typing import List, Any

from wwwpy.remote import rpc as rpc
from js import console


async def _setup_browser_dev_mode():
    from wwwpy.remote import micropip_install
    from wwwpy.common import designer

    from wwwpy.common.filesystem.sync import sync_delta2
    from wwwpy.common.filesystem.sync import Sync
    sync_impl: Sync = sync_delta2

    for package in designer.pypi_packages:
        await micropip_install(package)

    def file_changed(events: List[Any]):
        from wwwpy.remote.root_path import _get_dir
        wd = _get_dir()
        sync_impl.sync_target(wd.root, events)

        from wwwpy.remote.browser_main import _reload
        _reload()

    rpc.file_changed_listeners_add(file_changed)
