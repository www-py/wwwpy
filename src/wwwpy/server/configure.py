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


def start_default(port: int, directory: Path):
    webserver = available_webservers().new_instance()

    convention(directory, webserver)

    webserver.set_port(port).start_listen()
    wait_forever()




websocket_pool: WebsocketPool = None


def convention(directory: Path, webserver: Webserver) -> List[HttpRoute]:
    """
    Convention for a wwwpy server.
    It configures the webserver to serve the files from the working directory.
    It also configures the webserver to serve the files from the library.
    """
    print(f'applying convention to working_dir: {directory}')
    sys.path.insert(0, str(directory))
    sys.meta_path.insert(0, CustomFinder())
    global websocket_pool
    websocket_pool = WebsocketPool('/wwwpy/ws')
    services = configure_services('/wwwpy/rpc')
    routes = [services.route, websocket_pool.http_route, *bootstrap_routes(
        resources=[
            library_resources(),
            services.remote_stub_resources(),
            from_directory(directory / 'remote', relative_to=directory),
            from_directory(directory / 'common', relative_to=directory),
            from_file(directory / 'common.py', relative_to=directory),
            from_file(directory / 'remote.py', relative_to=directory),
        ],
        python=f'from wwwpy.remote.main import entry_point; await entry_point()'
    )]

    if webserver is not None:
        webserver.set_http_route(*routes)

    return routes
