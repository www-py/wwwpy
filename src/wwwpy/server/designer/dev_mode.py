from __future__ import annotations

from datetime import timedelta
from typing import List

import wwwpy.remote.rpc as rpc
from wwwpy.common import modlib
from wwwpy.common.filesystem import sync
from wwwpy.common.filesystem.sync import Sync
from wwwpy.common.filesystem.sync import filesystemevents_print
from wwwpy.common.filesystem.sync import sync_delta2
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer
from wwwpy.websocket import WebsocketPool

sync_impl: Sync = sync_delta2


def _watch_filesystem_change_for_remote(package: str, websocket_pool: WebsocketPool):
    directory = modlib._find_package_directory(package)
    if not directory:
        return

    def on_sync_events(events: List[sync.Event]):
        try:
            filesystemevents_print(events)
            payload = sync_impl.sync_source(directory, events)
            for client in websocket_pool.clients:
                remote_rpc = client.rpc(rpc.BrowserRpc)
                remote_rpc.package_file_changed_sync(package, payload)
        except:
            # we could send a sync_init
            import traceback
            print(f'on_sync_events 1 {traceback.format_exc()}')

    handler = WatchdogDebouncer(directory, timedelta(milliseconds=100), on_sync_events)
    handler.watch_directory()


def _watch_filesystem_for_local_reload(package: str):
    directory = modlib._find_module_path(package)
    if not directory:
        return

    def on_sync_events(events: List[sync.Event]):
        import wwwpy.common.reloader as reloader
        try:
            filesystemevents_print(events)
            reloader.unload_path(str(directory))
        except:
            # we could send a sync_init
            import traceback
            print(f'on_sync_events 2 {traceback.format_exc()}')

    handler = WatchdogDebouncer(directory, timedelta(milliseconds=100), on_sync_events)
    handler.watch_directory()


def _dev_mode(remote_packages: list[str], rpc_server_allowed: list[str], websocket_pool: WebsocketPool):
    for package in remote_packages:
        _watch_filesystem_change_for_remote(package, websocket_pool)

    for module_name in rpc_server_allowed:
        _watch_filesystem_for_local_reload(module_name)
