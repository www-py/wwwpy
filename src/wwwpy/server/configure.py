from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common.rpc.custom_loader import CustomFinder
from wwwpy.http import HttpRoute
from wwwpy.resources import library_resources, from_directory, from_file
from wwwpy.server.rpc import configure_services
from wwwpy.webserver import wait_forever, Webserver
from wwwpy.webservers.available_webservers import available_webservers
from wwwpy.websocket import WebsocketPool


def start_default(port: int, directory: Path, dev_mode=False):
    webserver = available_webservers().new_instance()

    convention(directory, webserver, dev_mode=dev_mode)

    webserver.set_port(port).start_listen()
    wait_forever()


websocket_pool: WebsocketPool = None


def convention(directory: Path, webserver: Webserver, dev_mode=False) -> List[HttpRoute]:
    print(f'applying convention to working_dir: {directory}')
    sys.path.insert(0, str(directory))
    sys.meta_path.insert(0, CustomFinder({'remote', 'remote.rpc', 'wwwpy.remote', 'wwwpy.remote.rpc'}))
    global websocket_pool
    websocket_pool = WebsocketPool('/wwwpy/ws')
    services = configure_services('/wwwpy/rpc')
    browser_dir = directory / 'remote'
    routes = [services.route, websocket_pool.http_route, *bootstrap_routes(
        resources=[
            library_resources(),
            services.remote_stub_resources(),
            from_directory(browser_dir, relative_to=directory),
            from_directory(directory / 'common', relative_to=directory),
            from_file(directory / 'common.py', relative_to=directory),  # remove .py support
            from_file(directory / 'remote.py', relative_to=directory),  # remove .py support
        ],
        python=f'from wwwpy.remote.main import entry_point; await entry_point(dev_mode={dev_mode})'
    )]

    if dev_mode:
        import wwwpy.remote.rpc as rpc
        import asyncio
        from wwwpy.server import watcher

        def on_file_changed(path: Path):
            path = Path(path)
            if path.is_dir() or path == directory:
                return
            rel_path = path.relative_to(directory)
            print(f'clients len: {len(websocket_pool.clients)} file changed: {rel_path}')
            for client in websocket_pool.clients:
                remote_rpc = client.rpc(rpc.BrowserRpc)
                remote_rpc.file_changed(str(rel_path), path.read_text())

        def on_file_changed_loop(path: Path):
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(on_file_changed, path)

        # watcher._watch_directory(browser_dir, on_file_changed_loop)
        watcher._watch_directory(browser_dir, on_file_changed)

    if webserver is not None:
        webserver.set_http_route(*routes)

    return routes
