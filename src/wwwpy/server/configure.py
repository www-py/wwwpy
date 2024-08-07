from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common.quickstart import _setup_quickstart
from wwwpy.common.rpc.custom_loader import CustomFinder
from wwwpy.resources import library_resources, from_directory, from_file
from wwwpy.server.rpc import configure_services
from wwwpy.webserver import Webserver
from wwwpy.webservers.available_webservers import available_webservers
from wwwpy.websocket import WebsocketPool


def start_default(port: int, directory: Path, dev_mode=False):
    webserver = available_webservers().new_instance()

    convention(directory, webserver, dev_mode=dev_mode)

    webserver.set_port(port).start_listen()


websocket_pool: WebsocketPool = None


# todo convention(dev_mode=True) without a ./remote folder fails
def convention(directory: Path, webserver: Webserver = None, dev_mode=False):
    print(f'applying convention to working_dir: {directory}')
    if dev_mode:
        if not any(directory.iterdir()):
            print(f'empty directory, creating quickstart in {directory.absolute()}')
            _setup_quickstart(directory)
    sys.path.insert(0, str(directory))
    sys.meta_path.insert(0, CustomFinder({'remote', 'remote.rpc', 'wwwpy.remote', 'wwwpy.remote.rpc'}))
    global websocket_pool
    websocket_pool = WebsocketPool('/wwwpy/ws')
    services = configure_services('/wwwpy/rpc')
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
        from wwwpy.server import watcher
        from watchdog.events import FileSystemEvent

        def on_file_changed(event: FileSystemEvent):
            # todo if this throws an exception, the hot reload stops
            try:
                path = Path(event.src_path)
                if path.is_dir() or path == directory:
                    return
                rel_path = path.relative_to(directory)
                content = None if path.is_dir() or not path.exists() else path.read_text()
                print(f'{datetime.now()} clients len: {len(websocket_pool.clients)} file changed: {rel_path}')
                for client in websocket_pool.clients:
                    remote_rpc = client.rpc(rpc.BrowserRpc)
                    remote_rpc.file_changed(event.event_type, str(rel_path).replace('\\', '/'), content)
            except:
                import traceback
                print(f'on_file_changed {traceback.format_exc()}')

        handler = watcher.ChangeHandler(directory, on_file_changed)
        handler.watch_directory()

    if webserver is not None:
        webserver.set_http_route(*routes)
