from __future__ import annotations

import sys
from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.server.custom_str import CustomStr
from wwwpy.common.designer import log_emit
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
    server_rpc_packages = ['server.rpc']
    remote_rpc_packages = {'remote', 'remote.rpc', 'wwwpy.remote', 'wwwpy.remote.rpc'}
    if dev_mode:
        server_rpc_packages.append('wwwpy.server.designer.rpc')
        remote_rpc_packages.add('wwwpy.remote.designer')
        remote_rpc_packages.add('wwwpy.remote.designer.rpc')
        log_emit.add_once(print)
        from wwwpy.common import quickstart
        quickstart._make_hotreload_work(directory)

    sys.path.insert(0, CustomStr(directory))
    sys.meta_path.insert(0, CustomFinder(remote_rpc_packages))
    global websocket_pool
    websocket_pool = WebsocketPool('/wwwpy/ws')
    services = _configure_server_rpc_services('/wwwpy/rpc', server_rpc_packages)
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
        from wwwpy.server.designer import dev_mode as dv
        dv._hotreload_remote(['common', 'remote'], websocket_pool)
        dv._hotreload_server(['common', 'server'])

    if webserver is not None:
        webserver.set_http_route(*routes)


from wwwpy.rpc import RpcRoute


def _configure_server_rpc_services(route_path: str, modules: list[str]) -> RpcRoute:
    services = RpcRoute(route_path)

    for module_name in modules:
        try:
            services.add_module(module_name)
        except Exception as e:
            print(f'could not load rpc module `{module_name}`: {e}')
            return None

    return services
