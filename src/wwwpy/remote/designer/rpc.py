from typing import List, Any

from wwwpy.common import modlib


class DesignerRpc:

    def package_file_changed_sync(self, package_name: str, events: List[Any]):
        from wwwpy.common.filesystem.sync import sync_delta2
        from wwwpy.common.filesystem.sync import Sync
        sync_impl: Sync = sync_delta2
        directory = modlib._find_package_directory(package_name)
        sync_impl.sync_target(directory, events)

        from wwwpy.remote.browser_main import _reload
        _reload()
