from __future__ import annotations

from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common import iterlib
from wwwpy.resources import library_resources, from_filesystem, from_filepath
from wwwpy.rpc import Services, Module, Stubber
from wwwpy.webserver import Webserver, wait_forever
from wwwpy.webservers.available_webservers import available_webservers


def start_default(port: int, directory: Path):
    webserver = available_webservers().new_instance()

    convention(directory, webserver)

    webserver.set_port(port).start_listen()
    wait_forever()


def convention(directory, webserver):
    """
    Convention for a wwwpy server.
    It configures the webserver to serve the files from the working directory.
    It also configures the webserver to serve the files from the library.
    """
    print(f'applying convention to working_dir: {directory}')
    import sys
    sys.path.insert(0, str(directory))
    stubber_resources = []
    try:
        import server.rpc as rpc_module
        services = Services()
        rpc_module = Module(rpc_module)
        services.add_module(rpc_module)
        webserver.set_http_route(services.route)

        stubber_resources = [Stubber(services.route.path, services, rpc_module).remote_stub_resources()]
    except:
        pass

    resources = iterlib.repeatable_chain(
        library_resources(),
        from_filesystem(directory / 'remote', relative_to=directory),
        from_filesystem(directory / 'common', relative_to=directory),
        from_filepath(directory / 'common.py', relative_to=directory),
        from_filepath(directory / 'remote.py', relative_to=directory),
        *stubber_resources,
    )
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python))

    return webserver
