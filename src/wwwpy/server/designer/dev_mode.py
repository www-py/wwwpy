from __future__ import annotations

from datetime import timedelta
from functools import partial
from typing import List, Callable

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
            filesystemevents_print(events, package)
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


def _hotreload_remote(remote_packages: list[str], websocket_pool: WebsocketPool, ):
    for package in remote_packages:
        _watch_filesystem_change_for_remote(package, websocket_pool)


def _watch_filesystem_change_for_server(package: str, callback: Callable[[str, List[sync.Event]], None]):
    directory = modlib._find_package_directory(package)
    if not directory:
        return

    def on_sync_events(events: List[sync.Event]):
        try:
            filesystemevents_print(events)
            callback(package, events)
        except:
            import traceback
            print(f'_watch_filesystem_change_for_server {traceback.format_exc()}')

    handler = WatchdogDebouncer(directory, timedelta(milliseconds=100), on_sync_events)
    handler.watch_directory()


def _hotreload_server(hotreload_packages: list[str]):
    def on_change(package: str, events: List[sync.Event]):

        for p in hotreload_packages:
            directory = modlib._find_package_directory(p)
            if directory:
                try:
                    import wwwpy.common.reloader as reloader
                    reloader.unload_path(str(directory))
                except:
                    # we could send a sync_init
                    import traceback
                    print(f'_hotreload_server {traceback.format_exc()}')

    for package in hotreload_packages:
        _watch_filesystem_change_for_server(package, on_change)
