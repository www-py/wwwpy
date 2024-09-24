from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common.filesystem.sync import filesystemevents_print
from wwwpy.common.quickstart import _setup_quickstart
from wwwpy.common.rpc.custom_loader import CustomFinder
from wwwpy.resources import library_resources, from_directory, from_file
from wwwpy.server.filesystem_sync.watchdog_debouncer import WatchdogDebouncer
from wwwpy.webserver import Webserver
from wwwpy.webservers.available_webservers import available_webservers
from wwwpy.websocket import WebsocketPool


def start_default(port: int, directory: Path, dev_mode=False):
    webserver = available_webservers().new_instance()

    convention(directory, webserver, dev_mode=dev_mode)

    webserver.set_port(port).start_listen()


websocket_pool: WebsocketPool = None


def convention(directory: Path, webserver: Webserver = None, dev_mode=False):
    print(f'applying convention to working_dir: {directory}')
    if dev_mode:
        if not any(directory.iterdir()):
            print(f'empty directory, creating quickstart in {directory.absolute()}')
            _setup_quickstart(directory)
        else:
            (directory / 'remote').mkdir(exist_ok=True)
            
    sys.path.insert(0, str(directory))
    sys.meta_path.insert(0, CustomFinder({'remote', 'remote.rpc', 'wwwpy.remote', 'wwwpy.remote.rpc'}))
    global websocket_pool
    websocket_pool = WebsocketPool('/wwwpy/ws')
    services = _configure_services('/wwwpy/rpc')
    routes = [services.route, websocket_pool.http_route, *bootstrap_routes(
        resources=[
            library_resources(),
            services.remote_stub_resources(),
            from_directory(directory / 'remote', relative_to=directory),
            from_directory(directory / 'common', relative_to=directory),
            from_file(directory / 'common.py', relative_to=directory),  # remove .py support
            from_file(directory / 'remote.py', relative_to=directory),  # remove .py support
        ],
        # language=python
        python=f'from wwwpy.remote.browser_main import entry_point; await entry_point(dev_mode={dev_mode})'
    )]

    if dev_mode:
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

    if webserver is not None:
        webserver.set_http_route(*routes)


from wwwpy.rpc import RpcRoute, Module


def _configure_services(route_path: str) -> RpcRoute:
    services = RpcRoute(route_path)
    try:
        import server.rpc
        services.add_module(Module(server.rpc))
    except Exception as e:
        print(f'could not load rpc module: {e}')
    return services
