from __future__ import annotations

from pathlib import Path
from typing import List

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.http import HttpRoute
from wwwpy.resources import library_resources, from_directory, from_file, ResourceIterable
from wwwpy.rpc import Services, Module
from wwwpy.server.rpc import configure_services
from wwwpy.webserver import wait_forever, Webserver
from wwwpy.webservers.available_webservers import available_webservers


def start_default(port: int, directory: Path):
    webserver = available_webservers().new_instance()

    convention(directory, webserver)

    webserver.set_port(port).start_listen()
    wait_forever()


def convention(directory: Path, webserver: Webserver) -> List[HttpRoute]:
    """
    Convention for a wwwpy server.
    It configures the webserver to serve the files from the working directory.
    It also configures the webserver to serve the files from the library.
    """
    print(f'applying convention to working_dir: {directory}')
    import sys
    sys.path.insert(0, str(directory))
    routes = []
    resources = []
    services = configure_services()
    routes.append(services.route)
    resources.extend(services.remote_stub_resources())

    resources.extend(_conventional_resources(directory))
    resources.append(library_resources())
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    routes.extend(bootstrap_routes(resources, python=bootstrap_python))

    if webserver is not None:
        webserver.set_http_route(*routes)

    return routes


def _conventional_resources(directory: Path, relative_to: Path = None) -> List[ResourceIterable]:
    if relative_to is None:
        relative_to = directory

    return [
        from_directory(directory / 'remote', relative_to=relative_to),
        from_directory(directory / 'common', relative_to=relative_to),
        from_file(directory / 'common.py', relative_to=relative_to),
        from_file(directory / 'remote.py', relative_to=relative_to),
    ]
