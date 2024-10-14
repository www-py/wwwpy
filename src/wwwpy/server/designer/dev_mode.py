from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import List, Callable, Set

from wwwpy.common import modlib, files
from wwwpy.common.filesystem import sync
from wwwpy.common.filesystem.sync import Sync
from wwwpy.common.filesystem.sync import filesystemevents_print
from wwwpy.common.filesystem.sync import sync_delta2
from wwwpy.remote.designer.rpc import DesignerRpc
from wwwpy.server.filesystem_sync.any_observer import logger
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer
from wwwpy.websocket import WebsocketPool, PoolEvent

sync_impl: Sync = sync_delta2

import logging

logger = logging.getLogger(__name__)


def _watch_filesystem_change_for_remote(package: str, websocket_pool: WebsocketPool):
    directory = modlib._find_package_directory(package)
    if not directory:
        return

    def on_sync_events(events: List[sync.Event]):
        try:
            filesystemevents_print(events, package)
            payload = sync_impl.sync_source(directory, events)
            for client in websocket_pool.clients:
                remote_rpc = client.rpc(DesignerRpc)
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
            # oh, boy. When a .py file is saved it fires the first hot reload. Then, when that file is loaded
            # the python updates the __pycache__ files, firing another (unwanted) reload: the first was enough!
            filt_events = _remove(events, directory, files.directory_blacklist)
            if len(filt_events) > 0:
                filesystemevents_print(filt_events)
                callback(package, filt_events)
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


def _remove(events: List[sync.Event], directory: Path, black_list: Set[str]) -> List[sync.Event]:
    def reject(e: sync.Event) -> bool:
        p = Path(e.src_path).relative_to(directory)
        for part in p.parts:
            if part in black_list:
                return True
        return False

    return [e for e in events if not reject(e)]


def _warning_on_multiple_clients(websocket_pool: WebsocketPool):
    def pool_before_change(event: PoolEvent):
        client_count = len(websocket_pool.clients)
        if client_count > 1:
            logger.warning(f'WARNING: more than one client connected, total={client_count}')
        elif event.remove:
            # 0 or 1
            logger.warning(f'Connected client count: {client_count}')

    websocket_pool.on_after_change.append(pool_before_change)
