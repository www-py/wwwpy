from __future__ import annotations

from pathlib import Path
from typing import List

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.resources import library_resources, from_directory, from_file, \
    FilesystemIterable, ResourceIterable
from wwwpy.rpc import Services, Module, Stubber
from wwwpy.webserver import wait_forever
from wwwpy.webservers.available_webservers import available_webservers


def start_default(port: int, directory: Path):
    webserver = available_webservers().new_instance()

    _convention(webserver, directory)

    webserver.set_port(port).start_listen()
    wait_forever()


def _add_conventional_resources(resources: List[ResourceIterable], directory: Path, relative_to: Path = None):
    if relative_to is None:
        relative_to = directory

    resources.extend([
        from_directory(directory / 'remote', relative_to=relative_to),
        from_directory(directory / 'common', relative_to=relative_to),
        from_file(directory / 'common.py', relative_to=relative_to),
        from_file(directory / 'remote.py', relative_to=relative_to),
        *_conventional_resources_additional
    ])


def _convention(webserver, directory) -> List[ResourceIterable]:
    """
    Convention for a wwwpy server.
    It configures the webserver to serve the files from the working directory.
    It also configures the webserver to serve the files from the library.
    """
    print(f'applying convention to working_dir: {directory}')
    import sys
    sys.path.insert(0, str(directory))
    resources = []
    try:
        import server.rpc as rpc_module
        services = Services()
        rpc_module = Module(rpc_module)
        services.add_module(rpc_module)
        webserver.set_http_route(services.route)

        resources.append(Stubber(services.route.path, services, rpc_module).remote_stub_resources())
    except Exception as e:
        print(f'could not load rpc module: {e}')

    _add_conventional_resources(resources, directory)

    resources.append(library_resources())
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python))

    return resources


def _setup_default_bootrap(resources, webserver):
    resources.append(library_resources())
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python))


_conventional_resources_additional: List[FilesystemIterable] = []


def _conventional_resources_additional_append(filesystem_iterable: FilesystemIterable):
    _conventional_resources_additional.append(filesystem_iterable)
