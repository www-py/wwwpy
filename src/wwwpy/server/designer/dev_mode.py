from __future__ import annotations

from datetime import timedelta
from typing import List

from wwwpy.common.filesystem.sync import filesystemevents_print
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer
from wwwpy.websocket import WebsocketPool


def _dev_mode(directory, websocket_pool: WebsocketPool):
    import wwwpy.remote.rpc as rpc
    from wwwpy.common.filesystem import sync
    from wwwpy.common.filesystem.sync import sync_delta2
    from wwwpy.common.filesystem.sync import Sync
    sync_impl: Sync = sync_delta2

    def on_sync_events(events: List[sync.Event]):
        try:
            filesystemevents_print(events)
            payload = sync_impl.sync_source(directory, events)
            for client in websocket_pool.clients:
                remote_rpc = client.rpc(rpc.BrowserRpc)
                remote_rpc.file_changed_sync(payload)
        except:
            # we could send a sync_init
            import traceback
            print(f'on_sync_events {traceback.format_exc()}')

    handler = WatchdogDebouncer(directory / 'remote', timedelta(milliseconds=100), on_sync_events)
    handler.watch_directory()
