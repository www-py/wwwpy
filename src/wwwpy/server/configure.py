from __future__ import annotations

import sys
from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common.quickstart import _setup_quickstart
from wwwpy.common.rpc.custom_loader import CustomFinder
from wwwpy.resources import library_resources, from_directory, from_file
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
        from wwwpy.server.designer.dev_mode import _dev_mode
        _dev_mode(['common', 'remote'], websocket_pool)

    if webserver is not None:
        webserver.set_http_route(*routes)


from wwwpy.rpc import RpcRoute, Module


def _configure_services(route_path: str) -> RpcRoute:
    services = RpcRoute(route_path)

    def _import_by_name(module_name: str):
        try:
            import importlib
            mod = Module(importlib.import_module(module_name))
            services.add_module(mod)
        except Exception as e:
            print(f'could not load rpc module `{module_name}`: {e}')
            return None

    _import_by_name('wwwpy.server.rpc')
    _import_by_name('server.rpc')
    return services
